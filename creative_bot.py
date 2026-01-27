# Chat in Socratic mode (like socratic_bot.py)

# A button to “Add current Q to SRS” (stores it with an auto answer)

# A Quiz me feature which picks a random item from history and asks a question, then evaluates when you submit

# creative_bot.py
import streamlit as st
from google import genai
from dotenv import load_dotenv
import os, json, random
from datetime import datetime, timedelta

# ---------------- SETUP ----------------
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = "gemini-2.5-flash-lite"

CHAT_FILE = "creative_chat.json"
SRS_FILE = "creative_srs.json"

st.set_page_config(page_title="Creative Learning Bot", layout="wide")
st.title("Creative Learning System")
st.caption("Socratic learning + memory + revision + quiz engine")

# ---------------- STORAGE ----------------
def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# ---------------- SRS LOGIC ----------------
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

# ---------------- PROMPT ----------------
SOCRATIC_PROMPT = """
You are a Socratic tutor.
You must guide learning only by asking questions.
Do not provide direct answers unless explicitly requested by the user.
"""

# ---------------- UI LAYOUT ----------------
left, right = st.columns([3, 1])

# ---------------- CHAT SECTION ----------------
with left:
    st.header("Socratic Chat")

    if "chat" not in st.session_state:
        st.session_state.chat = []

    for msg in st.session_state.chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask a question")

    if user_input:
        st.session_state.chat.append({"role": "user", "content": user_input})

        chat_data = load_json(CHAT_FILE, {"interactions": []})

        contents = []
        contents.append(SOCRATIC_PROMPT)

        for it in chat_data["interactions"][-8:]:
            contents.append(f"User: {it['query']}")
            contents.append(f"Assistant: {it['response']}")

        contents.append(f"User: {user_input}")

        try:
            resp = client.models.generate_content(
                model=MODEL_NAME,
                contents=contents
            )
            reply = resp.text
        except Exception as e:
            reply = f"Model error: {e}"

        st.session_state.chat.append({"role": "assistant", "content": reply})

        chat_data["interactions"].append({
            "query": user_input,
            "response": reply,
            "time": datetime.now().isoformat()
        })

        save_json(CHAT_FILE, chat_data)
        st.rerun()

# ---------------- CONTROL PANEL ----------------
with right:
    st.header("Learning Tools")

    # Add last chat to SRS
    if st.button("Store last chat for revision"):
        chat_data = load_json(CHAT_FILE, {"interactions": []})
        if chat_data["interactions"]:
            last = chat_data["interactions"][-1]
            srs = load_json(SRS_FILE, {"items": []})
            srs["items"].append({
                "query": last["query"],
                "answer": last["response"],
                "level": 0,
                "last_reviewed": datetime.now().isoformat()
            })
            save_json(SRS_FILE, srs)
            st.success("Stored for revision.")
        else:
            st.warning("No chat data available.")

    # Quiz generator
    if st.button("Generate Quiz"):
        srs = load_json(SRS_FILE, {"items": []})
        if not srs["items"]:
            st.warning("No learning items available.")
        else:
            pick = random.choice(srs["items"])
            st.session_state.quiz_item = pick

            quiz_prompt = f"Create a conceptual quiz question based on: {pick['query']}. Do not include the answer."

            try:
                resp = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=[quiz_prompt]
                )
                st.session_state.quiz_question = resp.text
            except Exception as e:
                st.session_state.quiz_question = f"Model error: {e}"

    if "quiz_question" in st.session_state:
        st.markdown("### Quiz")
        st.markdown(st.session_state.quiz_question)

        user_ans = st.text_area("Your answer")

        if st.button("Submit Quiz Answer"):
            qi = st.session_state.quiz_item

            eval_prompt = f"""
            Topic: {qi['query']}
            Question: {st.session_state.quiz_question}
            Student Answer: {user_ans}

            Decide correctness.
            Start with 'Correct:' or 'Incorrect:' and give short feedback.
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

            srs = load_json(SRS_FILE, {"items": []})

            for i, it in enumerate(srs["items"]):
                if it["query"] == qi["query"]:
                    if evaluation.lower().startswith("correct"):
                        srs["items"][i]["level"] = min(it["level"] + 1, 4)
                    else:
                        srs["items"][i]["level"] = max(it["level"] - 1, 0)

                    srs["items"][i]["last_reviewed"] = datetime.now().isoformat()
                    break

            save_json(SRS_FILE, srs)

            del st.session_state.quiz_question
            del st.session_state.quiz_item
            st.success("Quiz evaluated and progress saved.")

    # SRS summary
    if st.button("Show revision store"):
        srs = load_json(SRS_FILE, {"items": []})
        if not srs["items"]:
            st.info("No stored items.")
        else:
            for it in srs["items"]:
                st.markdown(
                    f"- {it['query']} | Level {it['level']} | Next: {next_review_time(it).isoformat()}"
                )
