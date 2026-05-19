"""
ZORO Web Server — Flask frontend bridge for your existing ZORO backend.
Place this file inside your ZORO/ project folder alongside main.py.
Run: python web_server.py
Then open: http://localhost:5000 in Chrome
"""

import os
import sys
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

# ── Import your existing ZORO modules ──────────────────────────────────────
from brain import ZOROBrain
from memory import ZOROMemory
from tasks import TaskManager
from email_agent import EmailAgent

app = Flask(__name__)
CORS(app)

# ── Initialize ZORO brain & memory once at startup ─────────────────────────
print("\n🗡️  Starting ZORO Web Server...\n")
brain  = ZOROBrain()
memory = ZOROMemory()
tasks  = TaskManager()
email  = EmailAgent()
print("\n✅ ZORO Web Server ready! Open http://localhost:5000 in Chrome\n")


def process_command(user_input: str) -> str:
    """Mirror of main.py process_command — routes to correct handler."""
    if not user_input or not user_input.strip():
        return "I didn't catch that. Could you repeat?"

    memory_context = memory.get_user_context()
    task_type = brain.classify_task(user_input)
    print(f"📌 Task: {task_type} | Input: {user_input}")

    # ── EMAIL SEND ─────────────────────────────────────────────────────────
    if task_type == "email":
        contacts = memory.get_contacts()
        email_details = brain.extract_email_details(user_input, contacts)
        to = subject = body = ""
        body_lines = []
        in_body = False
        for line in email_details.strip().split('\n'):
            if line.startswith("TO:"):
                to = line.replace("TO:", "").strip()
            elif line.startswith("SUBJECT:"):
                subject = line.replace("SUBJECT:", "").strip()
            elif line.startswith("BODY:"):
                body = line.replace("BODY:", "").strip()
                in_body = True
            elif in_body:
                body_lines.append(line)
        if body_lines:
            body = body + "\n" + "\n".join(body_lines)
        if to and "@" in to and subject:
            result = email.send_email(to, subject, body)
            memory.remember(f"Sent email to {to} about: {subject}")
            return result
        else:
            return "I need a valid email address to send to. Can you tell me the recipient's email?"

    # ── READ EMAILS ─────────────────────────────────────────────────────────
    elif task_type == "read_email":
        emails = email.read_latest_emails(count=5)
        return brain.summarize_emails(emails)

    # ── ADD TASK ────────────────────────────────────────────────────────────
    elif task_type == "task":
        task_text = user_input.lower()
        for filler in ["add task", "remind me to", "todo", "remember to", "don't forget to", "add a task to"]:
            task_text = task_text.replace(filler, "").strip()
        result = tasks.add_task(task_text)
        memory.remember(f"Added task: {task_text}")
        return result

    # ── MORNING BRIEFING ────────────────────────────────────────────────────
    elif task_type == "briefing":
        unread = email.get_unread_count()
        task_summary = tasks.get_today_summary()
        memory.remember("User asked for morning briefing")
        return f"Good morning! Here's your daily briefing. You have {unread} unread emails. {task_summary}"

    # ── SAVE MEMORY ─────────────────────────────────────────────────────────
    elif task_type == "memory":
        memory.remember(user_input)
        return "Got it! I'll remember that."

    # ── GENERAL Q&A ─────────────────────────────────────────────────────────
    else:
        response = brain.think(user_input, memory_context, task_type)
        memory.remember(f"User asked: {user_input[:100]}")
        return response


# ── Routes ──────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"error": "Empty message"}), 400
    try:
        reply = process_command(user_message)
        return jsonify({"reply": reply})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/tasks", methods=["GET"])
def get_tasks():
    try:
        summary = tasks.get_today_summary()
        return jsonify({"tasks": summary})
    except Exception as e:
        return jsonify({"tasks": "Could not fetch tasks."})


@app.route("/status", methods=["GET"])
def status():
    return jsonify({"status": "online", "model": brain.fast_model})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
