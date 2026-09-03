class ExtractionError(Exception):
    """Raised when Gemini extraction fails even after retries."""
    pass


class UnsupportedFileTypeError(Exception):
    """Raised when an uploaded file isn't a type we can process."""
    pass