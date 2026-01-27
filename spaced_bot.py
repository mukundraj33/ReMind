# spaced_bot.py
import streamlit as st
from google import genai
from dotenv import load_dotenv
import os, json
from datetime import datetime, timedelta

# ---------------- SETUP ----------------
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = "gemini-2.5-flash-lite"
DATA_FILE = "spaced_history.json"

st.set_page_config(page_title="Spaced Repetition Bot", layout="centered")
st.title("Spaced Repetition Learning Bot")
st.caption("Stores questions with levels and schedules reviews using spaced repetition.")

# ---------------- JSON STORAGE ----------------
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"items": []}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"items": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_item(query, answer):
    data = load_data()
    data["items"].append({
        "query": query,
        "answer": answer,
        "level": 0,
        "last_reviewed": datetime.now().isoformat()
    })
    save_data(data)

# ---------------- SPACED REPETITION LOGIC ----------------
LEVEL_INTERVALS = {
    0: timedelta(minutes=10),
    1: timedelta(hours=1),
    2: timedelta(days=1),
    3: timedelta(days=3),
    4: timedelta(days=7)
}

def next_review_time(item):
    last = datetime.fromisoformat(item["last_reviewed"])
    interval = LEVEL_INTERVALS.get(int(item["level"]), timedelta(days=7))
    return last + interval

def get_due_items():
    now = datetime.now()
    due = []
    for item in load_data()["items"]:
        if now >= next_review_time(item):
            due.append(item)
    return due

# ---------------- UI: ADD ITEM ----------------
st.header("Add Learning Item")

with st.form("add_form"):
    query = st.text_area("Enter a question or concept")
    auto_answer = st.checkbox("Auto-generate answer using AI", value=True)
    submitted = st.form_submit_button("Add to Learning Store")

    if submitted and query.strip():
        if auto_answer:
            prompt = f"Give a concise and clear answer to: {query}"
            try:
                resp = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=[prompt]
                )
                answer = resp.text
            except Exception as e:
                answer = f"Model error: {e}"
        else:
            answer = ""

        add_item(query, answer)
        st.success("Item stored successfully.")

# ---------------- REVIEW SECTION ----------------
st.header("Review Due Items")

if "current_review" not in st.session_state:
    st.session_state.current_review = None

if st.button("Start Review"):
    due = get_due_items()
    if not due:
        st.info("No items due for review.")
    else:
        st.session_state.current_review = due[0]

if st.session_state.current_review:
    item = st.session_state.current_review
    st.subheader("Review Question")
    st.markdown(f"**Question:** {item['query']}")

    user_answer = st.text_area("Your answer")

    if st.button("Submit Review"):
        eval_prompt = f"""
        Question: {item['query']}
        Reference Answer: {item['answer']}
        Student Answer: {user_answer}

        Decide if the student's answer is correct.
        Start your response with 'Correct:' or 'Incorrect:' and a short explanation.
        """

        try:
            resp = client.models.generate_content(
                model=MODEL_NAME,
                contents=[eval_prompt]
            )
            evaluation = resp.text
        except Exception as e:
            evaluation = f"Evaluation error: {e}"

        st.markdown("### Evaluation")
        st.markdown(evaluation)

        data = load_data()

        for i, it in enumerate(data["items"]):
            if it["query"] == item["query"]:
                if evaluation.lower().startswith("correct"):
                    data["items"][i]["level"] = min(it["level"] + 1, 4)
                else:
                    data["items"][i]["level"] = max(it["level"] - 1, 0)

                data["items"][i]["last_reviewed"] = datetime.now().isoformat()
                break

        save_data(data)
        st.session_state.current_review = None
        st.success("Progress updated.")

# ---------------- ALL ITEMS ----------------
st.header("Stored Learning Items")

data = load_data()
if not data["items"]:
    st.info("No stored items.")
else:
    for item in data["items"]:
        st.markdown(
            f"- **{item['query']}** | Level: {item['level']} | Next Review: {next_review_time(item).isoformat()}"
        )
