# Re-Mind: Agentic AI Tutor for Memory Retention  
**WiDS 2025 – Mid-Term and End-Term Submission**

---

## 📌 Project Overview

**Re-Mind** is an agentic AI–based tutoring system designed to improve a learner’s memory retention through **timely questioning, guided reasoning, and spaced repetition**.  
Instead of behaving like a simple chatbot, the system **actively manages memory, schedules reviews, and adapts interaction strategies** to encourage long-term learning.

The project evolves across two phases:

- **Mid-Term**: Focus on *agentic behavior* such as autonomous quiz triggering based on time or interaction count.
- **End-Term**: Extension into *persistent memory*, *Socratic tutoring*, *spaced repetition*, and *adaptive quizzing* using local storage.

The system is implemented using **Python**, **Streamlit**, and the **Google Gemini API**.

---

## 🧠 Agentic AI in Re-Mind

In this project, agentic AI refers to systems that:

- Maintain **state and memory**
- Make **decisions without explicit user commands**
- Interact with users **over time**
- Adapt behavior based on predefined rules

In Re-Mind:
- The **Gemini LLM** acts as the reasoning and evaluation engine
- The application maintains **short-term memory** using Streamlit session state
- The application maintains **long-term memory** using JSON-based local storage
- Decision logic determines:
  - when to quiz the user
  - how to guide the user (Socratic questioning)
  - when an item is due for revision
  - how learning difficulty evolves over time

---

## 📁 Repository Structure

- **ReMind/**
  - **app.py**  
    (Simple LLM chatbot)

  - **socratic_bot.py**

  - **spaced_bot.py**

  - **creative_bot.py**
    (Final chatbot combining all features)

  - **counterbot.py**  
   

  - **timebot.py**  
    

  - **requirements.txt**  
   

  - **README.md**  
  

  - **.env**  
  

---

## 🧩 File Descriptions

---

## 🔹 Mid-Term Components

### 1️⃣ `app.py` — Basic Chatbot

- Minimal chatbot using **Streamlit** and **Gemini API**
- Demonstrates:
  - API integration
  - environment variable usage
  - session-based conversation memory
- Serves as the **foundation** for all agentic extensions

---

### 2️⃣ `counterbot.py` — Query-Based Agent

- Tracks the **number of user queries**
- After **every 5 queries**:
  - selects recent conversation topics
  - generates **3 multiple-choice questions**
  - evaluates user answers
  - provides short explanations
- Resets counter after quiz completion

**Agentic behavior demonstrated:**
- state tracking
- autonomous quiz triggering
- rule-based decision making

---

### 3️⃣ `timebot.py` — Time-Based Agent

- Stores:
  - first user query
  - associated timestamp
- After **10 minutes**:
  - automatically generates a quiz
  - evaluates responses
- Resets once the quiz is completed

**Agentic behavior demonstrated:**
- time-based triggers
- delayed action
- memory-based questioning

---

## 🔹 End-Term Components

### 4️⃣ `socratic_bot.py` — Socratic Tutor with Persistent Memory

- Implements a **Socratic-style chatbot**
- The bot:
  - asks guiding questions instead of direct answers
  - avoids revealing solutions unless explicitly requested
- Stores conversation history in **local JSON files**
- Uses stored history as context for future interactions

**Key concepts demonstrated:**
- guided learning
- persistent memory beyond session lifetime
- context-aware reasoning

---

### 5️⃣ `spaced_bot.py` — Spaced Repetition Learning System

- Implements **spaced repetition theory**
- Each stored item contains:
  - `query`
  - `answer`
  - `level`
  - `last_reviewed` timestamp
- Review scheduling is based on:
  - item level
  - elapsed time since last review
- AI is used to:
  - generate reference answers
  - evaluate learner responses during review

**Key concepts demonstrated:**
- long-term memory management
- adaptive difficulty progression
- delayed recall for retention improvement

---

### 6️⃣ `creative_bot.py` — Integrated Learning System

- Combines multiple concepts into a single system:
  - Socratic tutoring
  - persistent chat memory
  - spaced repetition storage
  - adaptive quiz generation
- Allows:
  - storing meaningful chat interactions for revision
  - generating conceptual quiz questions
  - evaluating answers and updating learning levels

**Key concepts demonstrated:**
- multi-agent behavior
- system integration
- open-ended design choices

---

## 🛠️ Technologies Used

- **Python 3.10+**
- **Streamlit** — UI development and state management
- **Google Gemini API** — reasoning, question generation, and evaluation
- **dotenv** — secure API key management
- **JSON** — local persistent storage

---


---

## 🔮 Future Improvements

- Integrating a **database-backed storage system** (e.g., SQLite or PostgreSQL) to support scalability and concurrent users.
- Incorporating **user modeling** to personalize difficulty levels and review schedules based on individual learning patterns.
- Extending spaced repetition with **adaptive interval optimization** instead of fixed time gaps.
- Adding **multimodal inputs** such as PDFs or lecture notes to automatically generate learning items.
- Introducing **analytics dashboards** to visualize learning progress, retention rates, and performance trends.
- Enabling **multi-user authentication** to support personalized learning across devices.

---
