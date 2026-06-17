from fastapi import FastAPI, UploadFile, File
import os
import uuid

from services.pdf_service import load_and_validate_pdf
from services.vector_service import build_vector_db
from services.llm_service import generate_summary, ask_question

app = FastAPI()

SESSIONS = {}  # simple in-memory store

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        file_id = str(uuid.uuid4())
        file_path = f"temp_{file_id}.pdf"

        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Validate + process
        docs = load_and_validate_pdf(file_path)
        db, chunks = build_vector_db(docs, file_id)

        summary = generate_summary(chunks)

        SESSIONS[file_id] = db
        
        response = {
            "file_id": file_id,
            "summary": summary
        }
        os.remove(file_path)

        return response
    except Exception as e:
        print(e)
        return {
            "file_id": file_id,
            "summary": e
        }


@app.post("/ask")
async def ask(data: dict):
    file_id = data["file_id"]
    query = data["query"]

    db = SESSIONS.get(file_id)

    if not db:
        return {"error": "Session not found"}

    answer = ask_question(db, query)

    return {"answer": answer}