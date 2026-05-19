import os
from dotenv import load_dotenv
from voice import VoiceEngine
from brain import ZOROBrain
from memory import ZOROMemory
from email_agent import EmailAgent
from tasks import TaskManager

load_dotenv()

class ZORO:
    def __init__(self):
        print("\n🗡️  Initializing ZORO — Your Personal AI Assistant...\n")

        self.voice = VoiceEngine(
            use_elevenlabs=bool(os.getenv("ELEVENLABS_API_KEY")),
            elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY")
        )
        self.brain = ZOROBrain()
        self.memory = ZOROMemory()
        self.email_agent = EmailAgent()
        self.tasks = TaskManager()

        print("\n✅ ZORO is fully loaded and ready!\n")

    def process_command(self, user_input):
        """Process any user command and return a response"""
        if not user_input or not user_input.strip():
            return "I didn't catch that. Could you repeat?"

        print(f"\n📥 Processing: {user_input}")

        # Get memory context for personalization
        memory_context = self.memory.get_user_context()

        # Classify the task
        task_type = self.brain.classify_task(user_input)
        print(f"📌 Task type: {task_type}")

        # ── EMAIL SEND ──
        if task_type == "email":
            contacts = self.memory.get_contacts()
            email_details = self.brain.extract_email_details(user_input, contacts)

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
                result = self.email_agent.send_email(to, subject, body)
                self.memory.remember(f"Sent email to {to} about: {subject}")
                return result
            else:
                return "I need a valid email address to send to. Can you tell me the recipient's email?"

        # ── READ EMAILS ──
        elif task_type == "read_email":
            emails = self.email_agent.read_latest_emails(count=5)
            return self.brain.summarize_emails(emails)

        # ── ADD TASK ──
        elif task_type == "task":
            task_text = user_input.lower()
            for filler in ["add task", "remind me to", "todo", "remember to", "don't forget to", "add a task to"]:
                task_text = task_text.replace(filler, "").strip()
            result = self.tasks.add_task(task_text)
            self.memory.remember(f"Added task: {task_text}")
            return result

        # ── MORNING BRIEFING ──
        elif task_type == "briefing":
            unread = self.email_agent.get_unread_count()
            task_summary = self.tasks.get_today_summary()
            briefing = (
                f"Good morning! Here's your daily briefing. "
                f"You have {unread} unread emails. "
                f"{task_summary}"
            )
            self.memory.remember("User asked for morning briefing")
            return briefing

        # ── SAVE MEMORY ──
        elif task_type == "memory":
            self.memory.remember(user_input)
            return "Got it! I'll remember that."

        # ── GENERAL Q&A ──
        else:
            response = self.brain.think(user_input, memory_context, task_type)
            self.memory.remember(f"User asked: {user_input[:100]}")
            return response

    # ─────────────── TEXT MODE ───────────────
    def run_text_mode(self):
        print("\n" + "="*50)
        print("🗡️  ZORO TEXT MODE — Type your command")
        print("Type 'quit' to exit")
        print("="*50 + "\n")

        self.voice.speak("Hello! I am ZORO, your personal AI assistant. How can I help you today?")

        while True:
            try:
                user_input = input("You: ").strip()
            except (KeyboardInterrupt, EOFError):
                break

            if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                self.voice.speak("Goodbye! Have a great day!")
                break

            if not user_input:
                continue

            response = self.process_command(user_input)
            self.voice.speak(response)

    # ─────────────── VOICE MODE ───────────────
    def run_voice_mode(self):
        print("\n" + "="*50)
        print("🗡️  ZORO VOICE MODE — Say 'Hey ZORO' to start")
        print("Press Ctrl+C to exit")
        print("="*50 + "\n")

        self.voice.speak("Hello! I am ZORO. Say Hey ZORO to wake me up!")

        while True:
            try:
                # Wait for wake word
                self.voice.listen_for_wake_word()
                self.voice.speak("Yes? How can I help?")

                # Listen for command
                user_input = self.voice.listen()

                if not user_input:
                    self.voice.speak("I didn't catch that. Say Hey ZORO to try again.")
                    continue

                if any(w in user_input.lower() for w in ['goodbye', 'bye', 'stop', 'quit', 'exit']):
                    self.voice.speak("Goodbye! Have a great day!")
                    break

                response = self.process_command(user_input)
                self.voice.speak(response)

            except KeyboardInterrupt:
                print("\nShutting down ZORO...")
                break


# ─────────────── ENTRY POINT ───────────────
def main():
    zoro = ZORO()

    print("\n🗡️  Welcome to ZORO!")
    print("━"*30)
    print("1. Text Mode  (type commands)")
    print("2. Voice Mode (speak commands)")
    print("━"*30)

    choice = input("\nSelect mode (1 or 2): ").strip()

    if choice == "2":
        zoro.run_voice_mode()
    else:
        zoro.run_text_mode()


if __name__ == "__main__":
    main()
