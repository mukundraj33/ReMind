import streamlit as st
from google import genai
from dotenv import load_dotenv
import os

# Load local env variables for development. Streamlit Cloud should use
# app secrets instead of a committed .env file.
load_dotenv()

MODEL_NAME = "gemini-2.5-flash-lite"


def get_api_key():
    try:
        return st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    except Exception:
        return os.getenv("GEMINI_API_KEY")


api_key = get_api_key()

st.title("Re-Mind Chatbot")

if not api_key:
    st.error(
        "GEMINI_API_KEY is not configured. Add it in Streamlit Cloud under "
        "App settings > Secrets, or set it in a local .env file."
    )
    st.stop()

# Create Gemini client only after the key is available so deployment does not
# crash during module import.
client = genai.Client(api_key=api_key)

# Store chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
prompt = st.chat_input("Ask something...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        reply = response.text
    except Exception as e:
        reply = f"Error: {e}"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()
