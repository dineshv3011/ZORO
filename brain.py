import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class ZOROBrain:
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        # cascadeflow-style model routing
        # Simple tasks -> fast cheap model
        # Complex tasks -> powerful model
        self.fast_model = "llama-3.1-8b-instant"
        self.smart_model = "llama-3.3-70b-versatile"

        

        print("✅ ZORO Brain ready!")

    def classify_task(self, user_input):
        """Classify task type for cascadeflow model routing"""
        text = user_input.lower()

        if any(w in text for w in ["send", "email", "mail", "write to", "message to"]):
            return "email"
        elif any(w in text for w in ["read email", "check email", "inbox", "unread"]):
            return "read_email"
        elif any(w in text for w in ["remind", "add task", "todo", "remember to", "don't forget"]):
            return "task"
        elif any(w in text for w in ["morning", "briefing", "what's today", "my day", "schedule"]):
            return "briefing"
        elif any(w in text for w in ["what is", "who is", "explain", "how does", "tell me about", "define"]):
            return "qa"
        elif any(w in text for w in ["remember", "note", "save", "store"]):
            return "memory"
        else:
            return "general"

    def select_model(self, task_type):
        """
        cascadeflow routing logic:
        - Simple Q&A, tasks, memory → fast cheap model (saves cost)
        - Email drafting, briefing, complex tasks → smart model
        """
        if task_type in ["qa", "task", "memory", "general", "read_email"]:
            model = self.fast_model
            print(f"⚡ cascadeflow: Simple task → using fast model ({model})")
        else:
            model = self.smart_model
            print(f"🧠 cascadeflow: Complex task → escalating to smart model ({model})")
        return model

    def think(self, user_input, memory_context="", task_type="general"):
        """Main reasoning function"""
        model = self.select_model(task_type)

        system_prompt = f"""You are ZORO, a smart and friendly personal AI assistant.
You are helpful, concise, and speak naturally (your responses will be read aloud).

What you know about this user from memory:
{memory_context if memory_context else "No prior memory yet. This might be a new user."}

Guidelines:
- Keep responses short and natural for voice (2-4 sentences max for simple questions)
- Be warm, friendly and proactive
- For tasks and reminders, confirm clearly
- For general questions, be informative but brief
- Never use bullet points or markdown — speak naturally
"""
        try:
            response = self.groq_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=400,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Brain error: {e}")
            return "I had trouble processing that. Could you try again?"

    def extract_email_details(self, user_input, memory_context=""):
        """Extract TO, SUBJECT, BODY from a send email command"""
        prompt = f"""The user said: "{user_input}"

Known contacts from memory:
{memory_context}

Extract the email details and return EXACTLY in this format (nothing else):
TO: recipient_email@example.com
SUBJECT: subject line here
BODY: 
email body here
write it professionally"""

        try:
            response = self.groq_client.chat.completions.create(
                model=self.smart_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.5
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Email extraction error: {e}")
            return ""

    def summarize_emails(self, emails):
        """Summarize a list of emails in natural language"""
        if not emails:
            return "Your inbox is empty or I couldn't fetch emails."

        email_text = "\n".join([
            f"From: {e.get('From','Unknown')} | Subject: {e.get('Subject','No subject')}"
            for e in emails
        ])

        prompt = f"""Summarize these emails briefly in 2-3 sentences for a voice assistant:
{email_text}"""

        try:
            response = self.groq_client.chat.completions.create(
                model=self.fast_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150
            )
            return response.choices[0].message.content
        except:
            return f"You have {len(emails)} recent emails."
