import fitz
from langchain_core.documents import Document
from utils.config import render_page_to_jpeg_bytes, ocr_with_ocrspace

MAX_PAGES = 50
MIN_TEXT_LEN = 1

def load_and_validate_pdf(file_path):
    pdf = fitz.open(file_path)

    if pdf.page_count > MAX_PAGES:
        pdf.close()
        raise ValueError(f"PDF exceeds {MAX_PAGES} pages limit")

    docs = []

    for i, page in enumerate(pdf):
        text = page.get_text().strip()

        if len(text) < MIN_TEXT_LEN:
            print(f"Page {i} has insufficient text, performing OCR...")
            img_bytes = render_page_to_jpeg_bytes(page)
            text = ocr_with_ocrspace(img_bytes, language="auto").strip()

        if text:
            docs.append(Document(page_content=text, metadata={"page": i, "source": file_path}))

    pdf.close()

    if not docs:
        raise ValueError("No extractable text found in this PDF (even after OCR)")

    print(docs)
    return docs