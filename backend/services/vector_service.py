from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

def build_vector_db(docs, file_id):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(docs)

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-2"
    )

    db = Chroma.from_documents(
        chunks,
        embeddings,
        persist_directory=f"./db/chroma/{file_id}"
    )

    db.persist()

    return db, chunks