from unittest.mock import patch, MagicMock
import json
from app.extraction import extract_invoice_with_routing
from app.ai_config import MODEL_FLASH_LITE, MODEL_FLASH

# A deliberately broken extraction: line items sum to 100, but subtotal claims 999.
# This should fail validate_extraction() and force escalation to MODEL_FLASH.
BAD_RESULT = {
    "vendor_name": "Test Vendor",
    "invoice_number": "TEST-001",
    "invoice_date": "2026-01-01",
    "currency": "NOK",
    "subtotal": "999.00",   # wrong on purpose
    "vat_amount": "0.00",
    "total": "999.00",
    "line_items": [{"description": "Widget", "quantity": "1", "unit_price": "100.00", "amount": "100.00"}],
}

GOOD_RESULT = {
    **BAD_RESULT,
    "subtotal": "100.00",
    "total": "100.00",
}


def fake_response(data: dict):
    resp = MagicMock()
    resp.text = json.dumps(data)
    return resp


with patch("app.extraction.client.models.generate_content") as mock_generate, \
     patch("app.extraction.upload_file") as mock_upload:

    mock_upload.return_value = "fake-file-ref"
    # First call (Flash-Lite) returns bad math, second call (Flash) returns good math
    mock_generate.side_effect = [fake_response(BAD_RESULT), fake_response(GOOD_RESULT)]

    result = extract_invoice_with_routing("fake/path.pdf")

    assert result["_extraction_model"] == MODEL_FLASH, "should have escalated to Flash"
    assert result["_extraction_attempt"] == 2, "should have taken 2 attempts"
    assert mock_generate.call_count == 2

    print("✅ Escalation logic confirmed working:")
    print(f"   attempt 1 (Flash-Lite) failed validation as expected")
    print(f"   attempt 2 ({MODEL_FLASH}) succeeded and was returned")