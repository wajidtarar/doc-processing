import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.genai import errors as genai_errors


load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def upload_file(path: str, mime_type: str = "application/pdf"):
    """Uploads a file to Gemini's File API and returns a file reference
    the model can read directly — no OCR step needed."""
    return client.files.upload(file=path, config=types.UploadFileConfig(mime_type=mime_type))


logger = logging.getLogger("gemini")


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type((genai_errors.ServerError, genai_errors.ClientError)),
    reraise=True,
)
def call_gemini(model: str, contents: list, config) -> "types.GenerateContentResponse":
    """Retries on Gemini server/client errors (rate limits, timeouts, transient
    5xx) with exponential backoff: 1s, 2s, 4s. Does NOT retry on things like
    a malformed schema — reraise=True means after 3 failed attempts, the
    real exception propagates instead of being swallowed."""
    logger.info(f"Calling Gemini model={model}, prompt_chars={sum(len(str(c)) for c in contents if isinstance(c, str))}")
    response = client.models.generate_content(model=model, contents=contents, config=config)
    logger.info(f"Gemini response received, {len(response.text or '')} chars")
    return response