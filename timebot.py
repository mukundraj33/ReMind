import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os, json
from datetime import datetime, timedelta

QUIZ_DELAY_MINUTES = 10  

st.set_page_config(page_title="TimeBot", layout="centered")
load_dotenv()

MODEL = "gemini-2.5-flash-lite"

st.title("TimeBot ⏱️")
st.caption("Quiz after a fixed time delay")


def get_api_key():
    try:
        return st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    except Exception:
        return os.getenv("GEMINI_API_KEY")


API_KEY = get_api_key()
if not API_KEY:
    st.error(
        "GEMINI_API_KEY is not configured. Add it in Streamlit Cloud under "
        "App settings > Secrets, or set it in a local .env file."
    )
    st.stop()

client = genai.Client(api_key=API_KEY)


ss = st.session_state
def init(k, v):
    if k not in ss:
        ss[k] = v

init("chat", [])
init("msg_id", 0)
init("stored_query", None)
init("stored_time", None)
init("quiz_active", False)
init("mcqs", None)


def next_id():
    ss.msg_id += 1
    return ss.msg_id

def append(role, content, mid):
    if not any(m["id"] == mid for m in ss.chat):
        ss.chat.append({"id": mid, "role": role, "content": content})

def extract_json(text):
    try:
        return json.loads(text)
    except:
        s, e = text.find("["), text.rfind("]")
        if s != -1 and e != -1:
            try:
                return json.loads(text[s:e+1])
            except:
                return None
        return None


chat_box = st.container()

def render_chat():
    chat_box.empty()
    with chat_box:
        for m in ss.chat:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

render_chat()


with st.form("input_form", clear_on_submit=True):
    user_text = st.text_input("Ask something")
    send = st.form_submit_button("Send")

if send and user_text:
    uid = next_id()
    append("user", user_text, f"user_{uid}")

    if ss.stored_query is None:
        ss.stored_query = user_text
        ss.stored_time = datetime.now()

    append("assistant", "Saved. I’ll quiz you later.", f"assist_{uid}")
    render_chat()


if ss.stored_time and not ss.quiz_active:
    if datetime.now() - ss.stored_time >= timedelta(minutes=QUIZ_DELAY_MINUTES):
        prompt = f"""
Create EXACTLY 3 MCQs as JSON.
Topic: {ss.stored_query}

Same JSON format as before.
ONLY JSON.
"""
        try:
            r = client.models.generate_content(
                model=MODEL,
                contents=[types.Content(role="user", parts=[types.Part(text=prompt)])]
            )
            ss.mcqs = extract_json(r.text)
            ss.quiz_active = True
        except:
            pass

#  QUIZ
if ss.quiz_active and ss.mcqs:
    st.divider()
    st.subheader("📝 Time-Based Quiz")

    with st.form("quiz_form"):
        answers = {}
        for i, q in enumerate(ss.mcqs):
            st.markdown(f"**Q{i+1}. {q['question']}**")
            sel = st.radio(
                "",
                [f"A. {q['options'][0]}", f"B. {q['options'][1]}",
                 f"C. {q['options'][2]}", f"D. {q['options'][3]}"],
                key=f"q{i}"
            )
            answers[i] = sel[0]
        submit = st.form_submit_button("Submit")

    if submit:
        for i, q in enumerate(ss.mcqs):
            if answers[i] == q["answer"]:
                st.success(f"Q{i+1}: Correct")
            else:
                st.error(f"Q{i+1}: Incorrect")
            st.code(q["explanation"])

        ss.stored_query = None
        ss.stored_time = None
        ss.quiz_active = False
        ss.mcqs = None


#########################################################################
# # timebot.py
# import streamlit as st
# from google import genai
# from google.genai import types
# from dotenv import load_dotenv
# import os
# import json
# import random
# from datetime import datetime, timedelta

# # ---------------- Config ----------------
# QUIZ_DELAY_MINUTES = 1   # ⚠️ change to 1 for testing if needed

# st.set_page_config(page_title="TimeBot", layout="centered")
# load_dotenv()

# API_KEY = os.getenv("GEMINI_API_KEY")
# if not API_KEY:
#     st.error("GEMINI_API_KEY not found in .env")
#     st.stop()

# client = genai.Client(api_key=API_KEY)
# MODEL_NAME = "gemini-2.5-flash-lite"

# st.title("TimeBot ⏱️")
# st.caption("Quizzes you 10 minutes after you ask a question")

# # ---------------- Session State ----------------
# ss = st.session_state

# def init(key, val):
#     if key not in ss:
#         ss[key] = val

# init("chat", [])
# init("stored_query", None)
# init("stored_time", None)
# init("quiz_active", False)
# init("mcqs", None)
# init("quiz_done", False)

# # ---------------- Helpers ----------------
# def extract_json(text):
#     try:
#         return json.loads(text)
#     except Exception:
#         s = text.find("[")
#         e = text.rfind("]")
#         if s != -1 and e != -1:
#             try:
#                 return json.loads(text[s:e+1])
#             except Exception:
#                 return None
#         return None

# # ---------------- Show Chat ----------------
# for msg in ss.chat:
#     with st.chat_message(msg["role"]):
#         st.markdown(msg["content"])

# # ---------------- Input ----------------
# user_input = st.chat_input("Ask something...")

# if user_input:
#     ss.chat.append({"role": "user", "content": user_input})

#     # store first query time only
#     if ss.stored_query is None:
#         ss.stored_query = user_input
#         ss.stored_time = datetime.now()

#     # simple assistant reply (quota-safe)
#     ss.chat.append({
#         "role": "assistant",
#         "content": "Got it 👍 I’ll check your understanding later."
#     })

# # ---------------- Time Check ----------------
# if (
#     ss.stored_time
#     and not ss.quiz_active
#     and not ss.quiz_done
#     and datetime.now() - ss.stored_time >= timedelta(minutes=QUIZ_DELAY_MINUTES)
# ):
#     quiz_prompt = (
#         "Create exactly 3 multiple-choice questions based on the topic below.\n\n"
#         f"Topic: {ss.stored_query}\n\n"
#         "Each MCQ must have:\n"
#         "- question\n"
#         "- 4 options (A,B,C,D)\n"
#         "- correct answer letter\n"
#         "- explanation of exactly two short lines separated by a newline\n\n"
#         "Return ONLY a JSON array of 3 objects with keys: "
#         "question, options, answer, explanation."
#     )

#     with st.spinner("Generating quiz..."):
#         try:
#             resp = client.models.generate_content(
#                 model=MODEL_NAME,
#                 contents=[types.Content(
#                     role="user",
#                     parts=[types.Part(text=quiz_prompt)]
#                 )]
#             )
#             mcqs = extract_json(resp.text)
#             if mcqs and isinstance(mcqs, list):
#                 ss.mcqs = mcqs
#                 ss.quiz_active = True
#             else:
#                 st.error("Failed to generate quiz.")
#         except Exception as e:
#             st.error(f"Quiz generation failed: {e}")

# # ---------------- Quiz UI ----------------
# if ss.quiz_active and ss.mcqs:
#     st.divider()
#     st.subheader("📝 Time-Based Quiz")

#     with st.form("quiz_form"):
#         answers = {}
#         for i, q in enumerate(ss.mcqs):
#             st.markdown(f"**Q{i+1}. {q['question']}**")
#             opts = q["options"]
#             labels = [
#                 f"A. {opts[0]}",
#                 f"B. {opts[1]}",
#                 f"C. {opts[2]}",
#                 f"D. {opts[3]}"
#             ]
#             sel = st.radio("Choose:", labels, key=f"q{i}")
#             answers[i] = sel.split(".")[0]
#             st.write("")
#         submit = st.form_submit_button("Submit Answers")

#     if submit:
#         st.subheader("📊 Evaluation")
#         score = 0
#         for i, q in enumerate(ss.mcqs):
#             correct = q["answer"]
#             chosen = answers[i]
#             if chosen == correct:
#                 score += 1
#                 st.markdown(f"**Q{i+1}: Correct ✅**")
#             else:
#                 st.markdown(f"**Q{i+1}: Incorrect ❌ (Correct: {correct})**")
#             st.code(q["explanation"], language=None)

#         st.success(f"Score: {score} / 3")

#         # reset everything
#         ss.quiz_done = True
#         ss.quiz_active = False
#         ss.mcqs = None
#         ss.stored_query = None
#         ss.stored_time = None
