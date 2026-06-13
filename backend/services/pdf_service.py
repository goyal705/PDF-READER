from langchain_community.document_loaders import PyPDFLoader

MAX_PAGES = 50

def load_and_validate_pdf(file_path):
    loader = PyPDFLoader(file_path)
    docs = loader.load()

    if len(docs) > MAX_PAGES:
        raise ValueError("PDF exceeds 50 pages limit")

    return docs