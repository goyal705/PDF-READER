from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()


llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

def generate_summary(chunks):
    text = "\n".join([c.page_content for c in chunks[:20]])

    prompt = f"""
    Summarize this document:

    {text}

    Give:
    - Overview
    - Key points
    """

    return llm.invoke(prompt).content


def ask_question(db, query):
    retriever = db.as_retriever(search_kwargs={"k": 4})

    # ✅ FIX HERE
    docs = retriever.invoke(query)

    context = "\n".join([d.page_content for d in docs])

    prompt = f"""
    Answer using only this context:

    {context}

    Question: {query}
    """

    return llm.invoke(prompt).content