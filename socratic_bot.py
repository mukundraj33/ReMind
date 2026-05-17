# socratic_bot.py
import streamlit as st
from google import genai
from dotenv import load_dotenv
import os, json
from datetime import datetime

# ---------------- SETUP ----------------
load_dotenv()
MODEL_NAME = "gemini-2.5-flash-lite"
DATA_FILE = "socratic_history.json"

st.set_page_config(page_title="Socratic Bot", layout="centered")
st.title("Socratic Chatbot (Persistent JSON History)")
st.caption("I respond only with guiding questions unless you explicitly ask for a direct answer.")


def get_api_key():
    try:
        return st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    except Exception:
        return os.getenv("GEMINI_API_KEY")


api_key = get_api_key()
if not api_key:
    st.error(
        "GEMINI_API_KEY is not configured. Add it in Streamlit Cloud under "
        "App settings > Secrets, or set it in a local .env file."
    )
    st.stop()

client = genai.Client(api_key=api_key)

# ---------------- SOCratic PROMPT ----------------
SYSTEM_PROMPT = """
You are a Socratic tutor.
You MUST guide the user only by asking questions.
DO NOT give direct answers unless the user explicitly says:
"give me the answer" or "answer directly".
Keep questions short, logical, and progressive.
"""

# ---------------- JSON HELPERS ----------------
def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def save_interaction(q, a):
    data = load_data()
    data.append({
        "query": q,
        "response": a,
        "time": datetime.now().isoformat()
    })
    save_data(data)

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display current session messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------- USER INPUT ----------------
user_input = st.chat_input("Ask something...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})


    history = load_data()

   
    contents = []
    contents.append(f"SYSTEM INSTRUCTION:\n{SYSTEM_PROMPT}")

  
    for h in history[-8:]:
        contents.append(f"User: {h['query']}")
        contents.append(f"Assistant: {h['response']}")

    contents.append(f"User: {user_input}")

    # Call Gemini
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents
        )
        reply = response.text
    except Exception as e:
        reply = f"Model error: {e}"

    # Show reply
    st.session_state.messages.append({"role": "assistant", "content": reply})
    save_interaction(user_input, reply)

    st.rerun()

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("Saved History")
    if st.button("Show stored JSON history"):
        data = load_data()
        if not data:
            st.info("No stored interactions yet.")
        else:
            for item in data[-20:]:
                st.markdown(f"**Q:** {item['query']}")
                st.markdown(f"**A:** {item['response']}")
                st.caption(item["time"])
                st.markdown("---")

    if st.button("Download JSON"):
        st.download_button(
            "Download history",
            json.dumps(load_data(), indent=2),
            file_name="socratic_history.json"
        )
