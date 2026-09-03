from google.genai import types
from app.gemini_client import client, upload_file
from app.ai_config import MODEL_FLASH_LITE

from decimal import Decimal, InvalidOperation
from app.ai_config import MODEL_FLASH

from app.gemini_client import call_gemini
from app.exceptions import ExtractionError

import logging
logger = logging.getLogger("extraction")


# JSON schema Gemini is forced to conform to. Mirrors schemas.InvoiceCreate,
# with quantity as a string on purpose (see Phase 1 notes — "40 hrs", "12 months").
INVOICE_SCHEMA = {
    "type": "object",
    "properties": {
        "vendor_name": {"type": "string"},
        "invoice_number": {"type": "string"},
        "invoice_date": {"type": "string", "description": "ISO format YYYY-MM-DD"},
        "due_date": {"type": "string", "description": "ISO format YYYY-MM-DD"},
        "customer_reference": {"type": "string"},
        "currency": {"type": "string", "description": "3-letter currency code"},
        "subtotal": {"type": "string", "description": "decimal amount, no currency symbol"},
        "vat_rate": {"type": "string", "description": "percentage as decimal, e.g. '25.00'"},
        "vat_amount": {"type": "string"},
        "total": {"type": "string"},
        "line_items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "quantity": {"type": "string", "description": "keep units as written, e.g. '40 hrs', '12 months'"},
                    "unit_price": {"type": "string"},
                    "amount": {"type": "string"},
                },
                "required": ["description", "quantity", "unit_price", "amount"],
            },
        },
    },
    "required": [
        "vendor_name", "invoice_number", "invoice_date", "currency",
        "subtotal", "total", "line_items",
    ],
}

EXTRACTION_PROMPT = """Extract all invoice data from this document into the given schema.
Preserve quantity units exactly as written on the document (e.g. "40 hrs", "12 months", "25").
Use ISO format (YYYY-MM-DD) for all dates. Do not include currency symbols in amount fields."""


def extract_invoice(file_path: str, media_resolution: str = "MEDIA_RESOLUTION_HIGH") -> dict:
    uploaded = upload_file(file_path)

    response = client.models.generate_content(
        model=MODEL_FLASH_LITE,
        contents=[uploaded, EXTRACTION_PROMPT],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=INVOICE_SCHEMA,
            media_resolution=media_resolution,
        ),
    )
    import json
    return json.loads(response.text)


def validate_extraction(data: dict) -> list[str]:
    """Returns a list of problems found. Empty list = passes validation."""
    problems = []
    try:
        subtotal = Decimal(data["subtotal"])
        total = Decimal(data["total"])
        vat_amount = Decimal(data.get("vat_amount") or "0")
        line_sum = sum(Decimal(item["amount"]) for item in data["line_items"])

        if abs(line_sum - subtotal) > Decimal("0.01"):
            problems.append(f"line items sum to {line_sum}, but subtotal is {subtotal}")
        if abs((subtotal + vat_amount) - total) > Decimal("0.01"):
            problems.append(f"subtotal + vat ({subtotal + vat_amount}) != total ({total})")
    except (InvalidOperation, KeyError, TypeError) as e:
        problems.append(f"could not validate math: {e}")

    if not data.get("line_items"):
        problems.append("no line items extracted")

    return problems


def extract_invoice_with_routing(file_path: str) -> dict:
    """Try the cheap model first. If validation fails, escalate to the
    stronger model. This is the real 'route to cheap, escalate on failure'
    pattern — cheap to demo, genuinely used in production."""
    uploaded = upload_file(file_path)

    for attempt, model in enumerate([MODEL_FLASH_LITE, MODEL_FLASH]):
        try:
            response = call_gemini(
                model=model,
                contents=[uploaded, EXTRACTION_PROMPT],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=INVOICE_SCHEMA,
                    media_resolution="MEDIA_RESOLUTION_HIGH",
                ),
            )
        except Exception as e:
            logger.error(f"Gemini call failed after retries for model={model}: {e}")
            raise ExtractionError(f"Extraction failed after retries: {e}")

        import json
        data = json.loads(response.text)
        problems = validate_extraction(data)

        if not problems:
            data["_extraction_model"] = model
            data["_extraction_attempt"] = attempt + 1
            return data

        print(f"[routing] {model} failed validation: {problems}")

    # Both models failed validation — return the last attempt with warnings,
    # rather than silently pretending it's fine.
    data["_extraction_model"] = model
    data["_extraction_attempt"] = attempt + 1
    data["_validation_warnings"] = problems
    return data


SAVE_INVOICE_FUNCTION = types.FunctionDeclaration(
    name="save_extracted_invoice",
    description="Save the structured data extracted from an invoice document.",
    parameters=INVOICE_SCHEMA,
)

invoice_tool = types.Tool(function_declarations=[SAVE_INVOICE_FUNCTION])


def extract_invoice_via_function_call(file_path: str) -> dict:
    """Alternative to responseSchema: instead of returning raw JSON, Gemini
    decides to 'call' our save_extracted_invoice function with the extracted
    args. Useful once a model needs to choose between multiple possible
    actions, not just always return the same shape."""
    uploaded = upload_file(file_path)

    try:
        response = call_gemini(
            model=MODEL_FLASH_LITE,
            contents=[uploaded, EXTRACTION_PROMPT],
            config=types.GenerateContentConfig(
                tools=[invoice_tool],
                media_resolution="MEDIA_RESOLUTION_HIGH",
            ),
        )
    except Exception as e:
        logger.error(f"Gemini call failed after retries for model={MODEL_FLASH_LITE}: {e}")
        raise ExtractionError(f"Extraction failed after retries: {e}")

    call = response.candidates[0].content.parts[0].function_call
    if call is None or call.name != "save_extracted_invoice":
        raise ValueError(f"Expected a function call, got: {response.text}")

    return dict(call.args)

FLAG_PURCHASE_ORDER_FUNCTION = types.FunctionDeclaration(
    name="flag_as_purchase_order",
    description="Call this if the document is a purchase order, not an invoice — it authorizes a future purchase rather than billing for a completed one.",
    parameters={
        "type": "object",
        "properties": {
            "po_number": {"type": "string"},
            "vendor_name": {"type": "string"},
            "reason": {"type": "string", "description": "Brief note on what distinguishes it from an invoice"},
        },
        "required": ["reason"],
    },
)

FLAG_SPAM_FUNCTION = types.FunctionDeclaration(
    name="flag_as_spam_or_irrelevant",
    description="Call this if the document is not a business billing document at all — spam, an unrelated file, a resume, an article, etc.",
    parameters={
        "type": "object",
        "properties": {
            "reason": {"type": "string", "description": "Brief note on what the document actually appears to be"},
        },
        "required": ["reason"],
    },
)

classification_tool = types.Tool(
    function_declarations=[SAVE_INVOICE_FUNCTION, FLAG_PURCHASE_ORDER_FUNCTION, FLAG_SPAM_FUNCTION]
)


def classify_and_extract(file_path: str, mime_type: str = "application/pdf") -> dict:
    """Given an arbitrary uploaded document, let Gemini decide which of
    three actions applies, instead of assuming everything is an invoice.
    This is the real use case function calling is for — Phase 3 forced a
    single fixed shape, which responseSchema handled better."""
    uploaded = upload_file(file_path, mime_type=mime_type)

    try:
        response = call_gemini(
            model=MODEL_FLASH_LITE,
            contents=[uploaded, "Determine what kind of document this is and call the single most appropriate function."],
            config=types.GenerateContentConfig(tools=[classification_tool]),
        )
    except Exception as e:
        logger.error(f"Gemini call failed after retries for model={MODEL_FLASH_LITE}: {e}")
        raise ExtractionError(f"Extraction failed after retries: {e}")


    call = response.candidates[0].content.parts[0].function_call
    if call is None:
        return {"action": "unknown", "raw_response": response.text}

    return {"action": call.name, "args": dict(call.args)}