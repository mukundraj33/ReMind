# Re-Mind: Agentic AI Tutor for Memory Retention  
**WiDS 2025 – Mid-Term Submission**

---

## 📌 Project Overview

**Re-Mind** is an agentic AI–based tutoring system designed to improve a learner’s memory retention through **timely questioning and active recall**.  
Instead of behaving like a simple chatbot, the system **takes initiative** by deciding *when* to quiz the user and *what* to quiz them on, based on interaction count or time delay.

This project demonstrates the core ideas of **agentic AI**:
- maintaining state and memory,
- making decisions autonomously,
- interacting with users over time,
- using a Large Language Model (LLM) via an API.

The project is implemented using **Python**, **Streamlit**, and **Google Gemini API**.

---

## 🧠 What is Agentic AI (in this project)?

In Re-Mind:
- The **LLM (Gemini)** acts as the *reasoning engine*.
- The application maintains **memory** using Streamlit session state.
- The system follows **decision logic**:
  - when to interrupt normal conversation,
  - when to generate quizzes,
  - how to evaluate answers.

Instead of waiting passively for instructions, the system **acts on its own rules**, which makes it agentic.

---
## 📁 Repository Structure

- **ReMind/**
  - **app.py**  
    Simple LLM chatbot (Week 2 base implementation)

  - **counterbot.py**  
    Agent that triggers a quiz after every 5 user queries

  - **timebot.py**  
    Agent that triggers a quiz after a fixed time delay (10 minutes)

  - **requirements.txt**  
    List of Python dependencies required to run the project

  - **README.md**  
    Project documentation and setup instructions

  - **.env**  
    Stores the Gemini API key 

---
## 🧩 File Descriptions

### 1️⃣ `app.py` — Basic Chatbot
- A minimal chatbot using **Streamlit** and **Gemini API**
- Demonstrates:
  - API usage
  - environment variables
  - session-based chat memory
- Serves as the **foundation** for the agentic bots

---

### 2️⃣ `counterbot.py` — Query-Based Agent
- Maintains a **counter** of user questions
- After **every 5 questions**:
  - randomly selects recent topics
  - generates **3 MCQ questions**
  - evaluates user answers
  - provides **2-line explanations**
- Resets the counter after the quiz

**Agentic behavior demonstrated:**
- state tracking
- autonomous quiz triggering
- decision-making without explicit user command

---

### 3️⃣ `timebot.py` — Time-Based Agent
- Stores the **first user query and timestamp**
- After **10 minutes**:
  - automatically quizzes the user on that topic
  - generates 3 MCQs
  - evaluates answers with explanations
- Resets after quiz completion

**Agentic behavior demonstrated:**
- time-based decision logic
- delayed action
- memory retention testing

---

## 🛠️ Technologies Used

- **Python 3.10+**
- **Streamlit** — UI and state management
- **Google Gemini API** — LLM responses and quiz generation
- **dotenv** — secure API key handling

---