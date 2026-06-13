import os
import streamlit as st
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL")

st.set_page_config(page_title="Chat with PDF", layout="wide")

st.title("📄 Chat with your PDF")

# ---------------- SESSION STATE ---------------- #

if "file_id" not in st.session_state:
    st.session_state.file_id = None

if "processing" not in st.session_state:
    st.session_state.processing = False

if "messages" not in st.session_state:
    st.session_state.messages = []

if "summary" not in st.session_state:
    st.session_state.summary = ""

# ---------------- FILE UPLOAD ---------------- #

uploaded_file = st.file_uploader("Upload PDF (max 50 pages)", type=["pdf"])

if uploaded_file:

    if st.button("Process PDF", disabled=st.session_state.processing):
        st.session_state.processing = True
        st.rerun()

# ---------------- PROCESS PDF ---------------- #

if st.session_state.processing:

    with st.spinner("Processing PDF... ⏳"):

        res = requests.post(
            f"{API_URL}/upload",
            files={"file": uploaded_file}
        )

        if res.status_code == 200:
            data = res.json()

            st.session_state.file_id = data["file_id"]
            st.session_state.summary = data["summary"]

            # Add summary as first assistant message
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"📌 Summary:\n{data['summary']}"
            })

        else:
            st.error("❌ Error processing PDF")

    st.session_state.processing = False
    st.rerun()

# ---------------- CHAT UI ---------------- #

if st.session_state.file_id:

    st.divider()

    # Display chat messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input box at bottom (ChatGPT style)
    prompt = st.chat_input("Ask something about your PDF...")

    if prompt:

        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        # Show user message immediately
        with st.chat_message("user"):
            st.markdown(prompt)

        # Call API
        with st.chat_message("assistant"):
            with st.spinner("Thinking... 🤔"):

                res = requests.post(
                    f"{API_URL}/ask",
                    json={
                        "file_id": st.session_state.file_id,
                        "query": prompt
                    }
                )

                if res.status_code == 200:
                    answer = res.json()["answer"]
                else:
                    answer = "❌ Error getting response"

                st.markdown(answer)

        # Save assistant response
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })