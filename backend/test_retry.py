from unittest.mock import patch, MagicMock
from google.genai import errors as genai_errors
from app.gemini_client import call_gemini

call_count = {"n": 0}

def flaky_call(*args, **kwargs):
    call_count["n"] += 1
    if call_count["n"] < 3:
        raise genai_errors.ServerError("simulated transient failure", response_json={})
    resp = MagicMock()
    resp.text = '{"ok": true}'
    return resp

with patch("app.gemini_client.client.models.generate_content", side_effect=flaky_call):
    result = call_gemini(model="test-model", contents=["test"], config=None)
    print(f"Succeeded after {call_count['n']} attempts")
    print(f"Response: {result.text}")