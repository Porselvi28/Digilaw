import io
import os
from PIL import Image

try:
    import easyocr
except ImportError:
    easyocr = None

# We can reuse a single reader instance if we want, but it uses memory.
# For DigiLaw we will lazy load it on first use.
_reader = None

def get_reader():
    global _reader
    if _reader is None:
        if easyocr is None:
            raise ImportError("easyocr is not installed.")
        # Load English model. easyocr automatically uses GPU if available.
        # We suppress verbose output where possible.
        _reader = easyocr.Reader(['en'], gpu=True, verbose=False)
    return _reader

def extract_text_from_image_bytes(img_bytes: bytes) -> str:
    """
    Given raw bytes of an image, run OCR and return extracted text.
    """
    reader = get_reader()
    
    # easyocr can read directly from bytes in memory
    results = reader.readtext(img_bytes, detail=0, paragraph=True)
    return "\n\n".join(results)

def extract_text_from_image_file(file_path: str) -> str:
    """
    Given a path to an image file, run OCR and return extracted text.
    """
    reader = get_reader()
    results = reader.readtext(file_path, detail=0, paragraph=True)
    return "\n\n".join(results)
