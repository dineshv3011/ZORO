# 🗡️ ZORO — Your Personal AI Assistant
### Zero-latency Omni-Recall Oracle

ZORO is a smart personal AI assistant that remembers you, learns your habits,
and gets smarter with every interaction — powered by Hindsight memory and cascadeflow routing.

---

## ✨ Features
- 🎤 Voice Mode — say "Hey ZORO" to wake it up
- 💬 Text Mode — type your commands
- 📧 Send & read emails via Gmail
- 🧠 Remembers you across sessions (Hindsight)
- ⚡ Smart model routing to save costs (cascadeflow)
- 📋 Task & reminder management
- 🌅 Daily morning briefing
- 🔊 Natural voice replies (Edge TTS / ElevenLabs)

---

## 🚀 Setup

### 1. Install dependencies
pip install -r requirements.txt

### 2. Add your API keys
Copy .env.example to .env and fill in your keys:
- GROQ_API_KEY — from groq.com
- HINDSIGHT_API_KEY — from ui.hindsight.vectorize.io (use code MEMHACK515 for $50 free)
- ELEVENLABS_API_KEY — from elevenlabs.io (optional)

### 3. Add Gmail credentials
Place your downloaded credentials.json in the ZORO folder.

### 4. Run ZORO
python main.py

---

## 🗣️ Example Commands

| Command | What ZORO Does |
|---|---|
| "Hey ZORO" | Wakes up |
| "What is machine learning?" | Answers using AI |
| "Send an email to john@gmail.com about the meeting tomorrow" | Sends email |
| "Add task finish the presentation" | Saves task |
| "Good morning, what's my briefing?" | Daily summary |
| "Read my latest emails" | Summarizes inbox |
| "Remember that my manager is Priya" | Saves to memory |

---

## 🏗️ Tech Stack
- Groq — LLM brain
- Hindsight — persistent memory
- cascadeflow — smart model routing
- Whisper — speech to text
- Edge TTS / ElevenLabs — text to speech
- Gmail API — email
- SpeechRecognition — wake word & listening

---

