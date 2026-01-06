import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os, json, random


st.set_page_config(page_title="CounterBot", layout="centered")
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)
MODEL = "gemini-2.5-flash-lite"

st.title("CounterBot 🤖")
st.caption("Quiz after every 5 questions")

ss = st.session_state
def init(k, v):
    if k not in ss:
        ss[k] = v

init("chat", [])
init("msg_id", 0)
init("count", 0)
init("last_queries", [])
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
    submit = st.form_submit_button("Send")

if submit and user_text and not ss.quiz_active:
    uid = next_id()
    append("user", user_text, f"user_{uid}")

    ss.count += 1
    ss.last_queries.append(user_text)
    if len(ss.last_queries) > 5:
        ss.last_queries = ss.last_queries[-5:]

    # assistant reply
    try:
        r = client.models.generate_content(
            model=MODEL,
            contents=[types.Content(role="user", parts=[types.Part(text=user_text)])]
        )
        reply = r.text
    except:
        reply = "Noted 👍"

    append("assistant", reply, f"assist_{uid}")
    render_chat()

if ss.count == 5 and not ss.quiz_active:
    topics = random.sample(ss.last_queries, k=min(3, len(ss.last_queries)))
    prompt = f"""
Create EXACTLY 3 MCQs as JSON.
Topic(s): {topics}

Format:
[
 {{
  "question": "...",
  "options": ["A","B","C","D"],
  "answer": "A",
  "explanation": "line1\\nline2"
 }}
]
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
        ss.quiz_active = False

if ss.quiz_active and ss.mcqs:
    st.divider()
    st.subheader("📝 Quiz")

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
        submit_quiz = st.form_submit_button("Submit")

    if submit_quiz:
        score = 0
        for i, q in enumerate(ss.mcqs):
            if answers[i] == q["answer"]:
                score += 1
                st.success(f"Q{i+1}: Correct")
            else:
                st.error(f"Q{i+1}: Incorrect")
            st.code(q["explanation"])

        st.success(f"Score: {score}/3")

        ss.count = 0
        ss.last_queries = []
        ss.quiz_active = False
        ss.mcqs = None


################################################################
# # counterbot.py  (drop-in replacement)
# import streamlit as st
# from google import genai
# from google.genai import types
# from dotenv import load_dotenv
# import os
# import random
# import json
# import time

# # ---------------- Setup ----------------
# st.set_page_config(page_title="CounterBot - MCQ (fixed)", layout="centered")
# load_dotenv()
# API_KEY = os.getenv("GEMINI_API_KEY")
# if not API_KEY:
#     st.error("GEMINI_API_KEY not found in .env. Add it and rerun.")
#     st.stop()

# client = genai.Client(api_key=API_KEY)
# MODEL_NAME = "gemini-2.5-flash-lite"

# st.title("CounterBot — MCQ Quiz Mode")
# st.caption("Generates 3 MCQs after every 5 questions.")

# # ---------------- Session state init ----------------
# ss = st.session_state
# def init(key, val):
#     if key not in ss:
#         ss[key] = val

# init("count", 0)                  # queries since last quiz (0..4)
# init("total_questions", 0)        # total queries this session
# init("last_queries", [])          # last up-to-5 queries (strings)
# init("chat", [])                  # list of messages: {'id', 'role', 'content'}
# init("msg_id_counter", 0)         # integer id generator for inputs
# init("last_processed_input_id", None)  # avoid re-processing
# init("quiz_active", False)
# init("mcq_set", None)             # stored MCQs (list of dicts)
# init("mcq_answered", False)       # prevent double-evaluation

# # ---------------- Helpers ----------------
# def extract_json(text):
#     try:
#         return json.loads(text)
#     except Exception:
#         start = text.find('[')
#         end = text.rfind(']')
#         if start != -1 and end != -1 and end > start:
#             try:
#                 return json.loads(text[start:end+1])
#             except Exception:
#                 return None
#         return None

# def append_message(role, content, mid=None):
#     """Append message uniquely by id to avoid duplicates."""
#     if mid is None:
#         # create unique id for assistant messages if needed
#         ss["msg_id_counter"] += 1
#         mid = f"m{ss['msg_id_counter']}"
#     # check if id already present
#     for m in ss["chat"]:
#         if m["id"] == mid:
#             return
#     ss["chat"].append({"id": mid, "role": role, "content": content})

# # ---------------- Top counters / info ----------------
# col1, col2 = st.columns([1,1])
# with col1:
#     st.metric("Total queries (this session)", ss["total_questions"])
# with col2:
#     remaining = 5 - ss["count"]
#     st.metric("Queries until next quiz", remaining if remaining > 0 else 0)

# st.write("---")

# # ---------------- Chat display ----------------
# for msg in ss["chat"]:
#     # render in order stored
#     with st.chat_message(msg["role"]):
#         st.markdown(msg["content"])

# # ---------------- Input form (idempotent) ----------------
# with st.form(key="user_form", clear_on_submit=True):
#     user_text = st.text_input("Ask something (type and press Submit):")
#     submitted = st.form_submit_button("Submit")

# if submitted and user_text:
#     # create a stable id for this submission so reruns don't duplicate processing
#     ss["msg_id_counter"] += 1
#     input_id = f"in{ss['msg_id_counter']}"
#     # check if already processed
#     if ss["last_processed_input_id"] == input_id:
#         pass  # already handled
#     else:
#         ss["last_processed_input_id"] = input_id
#         # append user message (unique)
#         append_message("user", user_text, mid=input_id)

#         # update counters and last_queries
#         ss["count"] += 1
#         ss["total_questions"] += 1
#         ss["last_queries"].append(user_text)
#         if len(ss["last_queries"]) > 5:
#             ss["last_queries"] = ss["last_queries"][-5:]

#         # --- Assistant reply (either model or fallback) ---
#         with st.spinner("Assistant replying..."):
#             try:
#                 # To save quota, you can use fallback replies by uncommenting fallback behavior.
#                 # But here we attempt to call the model (will raise 429 if quota exhausted)
#                 response = client.models.generate_content(
#                     model=MODEL_NAME,
#                     contents=[types.Content(role="user", parts=[types.Part(text=user_text)])]
#                 )
#                 reply_text = response.text
#             except Exception as e:
#                 err = str(e)
#                 if "RESOURCE_EXHAUSTED" in err or "quota" in err.lower():
#                     reply_text = "Sorry — quota reached for model calls. Your question is recorded and will be used for future quizzes."
#                 else:
#                     reply_text = f"Error contacting model: {e}"
#         # assistant message id tied to input
#         append_message("assistant", reply_text, mid=f"resp_{input_id}")

#         # If we reached threshold and quiz not active, generate MCQs (only once)
#         if ss["count"] >= 5 and not ss["quiz_active"]:
#             # select topics (unique up to 3)
#             candidates = list(ss["last_queries"])
#             random.shuffle(candidates)
#             chosen = candidates[:3]

#             prompt = (
#                 "You are a strict exam question generator. Create exactly 3 multiple-choice questions "
#                 "based ONLY on the following topics (do not invent unrelated content):\n\n"
#                 f"{chosen}\n\n"
#                 "For each question output a JSON object with keys:\n"
#                 "  question: string\n"
#                 "  options: array of 4 strings (A,B,C,D in order)\n"
#                 "  answer: one of 'A','B','C','D'\n"
#                 "  explanation: two short lines separated by a newline (\\n)\n\n"
#                 "Return ONLY a JSON array of 3 such objects and nothing else."
#             )

#             with st.spinner("Generating 3 MCQs from last queries..."):
#                 try:
#                     mcq_resp = client.models.generate_content(
#                         model=MODEL_NAME,
#                         contents=[types.Content(role="user", parts=[types.Part(text=prompt)])]
#                     )
#                     raw = mcq_resp.text
#                     parsed = extract_json(raw)
#                     # fallback try
#                     if parsed is None or not isinstance(parsed, list) or len(parsed) != 3:
#                         time.sleep(0.5)
#                         alt = prompt + "\nNow output ONLY the JSON array, nothing else."
#                         mcq_resp2 = client.models.generate_content(
#                             model=MODEL_NAME,
#                             contents=[types.Content(role="user", parts=[types.Part(text=alt)])]
#                         )
#                         parsed = extract_json(mcq_resp2.text)
#                     if parsed is None:
#                         st.error("Failed to parse MCQs from model. Quiz cancelled.")
#                         ss["mcq_set"] = None
#                         ss["quiz_active"] = False
#                     else:
#                         # validate
#                         ok = True
#                         for item in parsed:
#                             if not all(k in item for k in ("question","options","answer","explanation")):
#                                 ok = False; break
#                             if not isinstance(item["options"], list) or len(item["options"])!=4:
#                                 ok=False; break
#                         if not ok:
#                             st.error("Model returned invalid MCQ structure. Quiz cancelled.")
#                             ss["mcq_set"] = None
#                             ss["quiz_active"] = False
#                         else:
#                             ss["mcq_set"] = parsed
#                             ss["quiz_active"] = True
#                             ss["mcq_answered"] = False
#                 except Exception as e:
#                     # handle quota gracefully
#                     err = str(e)
#                     if "RESOURCE_EXHAUSTED" in err or "quota" in err.lower():
#                         st.error("Quota exhausted while generating MCQs. Quiz cancelled for now.")
#                     else:
#                         st.error(f"Error generating MCQs: {e}")
#                     ss["mcq_set"] = None
#                     ss["quiz_active"] = False

# # ---------------- If quiz active: show MCQs (single form) ----------------
# if ss["quiz_active"] and ss["mcq_set"] and not ss["mcq_answered"]:
#     st.divider()
#     st.subheader("📝 MCQ Quiz (3 questions)")

#     with st.form("mcq_form"):
#         selections = {}
#         for i, q in enumerate(ss["mcq_set"]):
#             st.markdown(f"**Q{i+1}. {q['question']}**")
#             opts = q["options"]
#             labeled = [f"A. {opts[0]}", f"B. {opts[1]}", f"C. {opts[2]}", f"D. {opts[3]}"]
#             sel = st.radio("Choose one:", labeled, key=f"mcq_{i}")
#             selections[str(i)] = sel.split(".",1)[0].strip()
#             st.write("")
#         submit_mcq = st.form_submit_button("Submit MCQ answers")

#     if submit_mcq:
#         ss["mcq_answered"] = True
#         correct_count = 0
#         st.write("### Results")
#         for i, q in enumerate(ss["mcq_set"]):
#             selected = selections.get(str(i))
#             correct = q["answer"].strip().upper()
#             is_correct = (selected == correct)
#             if is_correct:
#                 correct_count += 1
#                 st.markdown(f"**Q{i+1} — Correct ✅**")
#             else:
#                 st.markdown(f"**Q{i+1} — Incorrect ❌** (You chose {selected}, correct is {correct})")
#             st.markdown("**Explanation:**")
#             st.code(q.get("explanation",""), language=None)

#         st.success(f"You scored {correct_count} out of 3")

#         # Reset after quiz (per spec)
#         ss["count"] = 0
#         ss["last_queries"] = []
#         ss["quiz_active"] = False
#         ss["mcq_set"] = None
#         ss["mcq_answered"] = False

# # ---------------- Sidebar: recent queries ----------------
# with st.sidebar:
#     st.header("Recent (last up to 5) queries")
#     if ss["last_queries"]:
#         for idx, qq in enumerate(reversed(ss["last_queries"]), 1):
#             st.write(f"{idx}. {qq}")
#     else:
#         st.write("_No recent queries_")
#     st.markdown("---")
#     st.caption("This bot generates MCQs after every 5 queries. If quota errors occur, the UI will show messages and not duplicate content.")
