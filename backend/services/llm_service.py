from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from dotenv import load_dotenv

load_dotenv()
search = DuckDuckGoSearchRun()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

def ask_from_web(query):
    results = search.run(query)

    prompt = f"""
    Answer the question using the web results below:

    {results}

    Question: {query}
    """

    return llm.invoke(prompt).content

def generate_summary(chunks):
    text = "\n".join([c.page_content for c in chunks[:20]])

    prompt = f"""
    Detect the primary language of the following text and answer in that language.
    Summarize this document:

    {text}

    Give:
    - Overview
    - Key points
    """

    return llm.invoke(prompt).content


def ask_question(db, query):
    retriever = db.as_retriever(search_kwargs={"k": 4})

    docs = retriever.invoke(query)

    # ✅ STEP 1: If no meaningful docs → fallback
    if not docs or all(len(d.page_content.strip()) < 30 for d in docs):
        return ask_from_web(query)

    context = "\n".join([d.page_content for d in docs])

    prompt = f"""
    Answer ONLY from the context below.
    If the answer is not present, say exactly: NOT_FOUND

    Context:
    {context}

    Question: {query}
    """

    response = llm.invoke(prompt).content.strip()

    # ✅ STEP 2: Smart fallback detection
    fallback_triggers = [
        "NOT_FOUND",
        "not contain",
        "not mentioned",
        "no information",
        "cannot find",
        "does not provide"
    ]

    if any(trigger.lower() in response.lower() for trigger in fallback_triggers):
        return ask_from_web(query)

    return response