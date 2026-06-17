import os
import io
import requests
import fitz  # pymupdf
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

OCR_API_KEY = os.environ["OCRSPACE_API_KEY"]  # never hardcode
MAX_OCR_FILE_BYTES = 1_000_000  # stay safely under the 1.5MB free cap


def render_page_to_jpeg_bytes(page, dpi=100, quality=85):
    """Render a fitz page to JPEG bytes, shrinking until under the size limit."""
    while True:
        pix = page.get_pixmap(dpi=dpi)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality)
        data = buf.getvalue()

        if len(data) <= MAX_OCR_FILE_BYTES or (dpi <= 60 and quality <= 50):
            return data

        # still too big -> reduce dpi first, then quality
        if dpi > 60:
            dpi -= 20
        else:
            quality -= 15


def ocr_with_ocrspace(image_bytes, language="auto"):
    response = requests.post(
        "https://api.ocr.space/parse/image",
        files={"file": ("page.jpg", image_bytes, "image/jpeg")},
        data={
            "apikey": OCR_API_KEY,
            "language": language,
            "OCREngine": 2,
            "isOverlayRequired": False,
        },
        timeout=60,
    )
    result = response.json()

    if result.get("IsErroredOnProcessing"):
        raise RuntimeError(f"OCR failed: {result.get('ErrorMessage')}")

    return result["ParsedResults"][0]["ParsedText"]


# usage on a scanned page:
# pdf = fitz.open(r"C:\Users\TusharGoyal\Downloads\Naac_appLetter.pdf")
# page = pdf[0]

# img_bytes = render_page_to_jpeg_bytes(page)
# text = ocr_with_ocrspace(img_bytes, language="auto")
# print(text)