import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def upload_file(path: str, mime_type: str = "application/pdf"):
    """Uploads a file to Gemini's File API and returns a file reference
    the model can read directly — no OCR step needed."""
    return client.files.upload(file=path, config=types.UploadFileConfig(mime_type=mime_type))