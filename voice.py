import os
import asyncio
import subprocess
import tempfile
import speech_recognition as sr
import edge_tts

class VoiceEngine:
    def __init__(self, use_elevenlabs=False, elevenlabs_api_key=None):
        self.recognizer = sr.Recognizer()
        self.use_elevenlabs = use_elevenlabs
        self.elevenlabs_api_key = elevenlabs_api_key
        self.wake_word = "zoro"
        self.voice = "en-US-GuyNeural"  # Edge TTS voice

    def listen_for_wake_word(self):
        """Listen continuously for 'Hey ZORO' wake word"""
        print("🎤 Listening for 'Hey ZORO'...")
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            while True:
                try:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=3)
                    text = self.recognizer.recognize_google(audio).lower()
                    print(f"Heard: {text}")
                    if self.wake_word in text:
                        print("✅ Wake word detected! ZORO is awake!")
                        return True
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    continue
                except Exception as e:
                    continue

    def listen(self):
        """Listen for a user command after wake word"""
        print("🎤 Listening for your command...")
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=15)
                text = self.recognizer.recognize_google(audio)
                print(f"You said: {text}")
                return text
            except sr.WaitTimeoutError:
                return None
            except sr.UnknownValueError:
                return None
            except Exception as e:
                print(f"Listen error: {e}")
                return None

    async def _speak_edge(self, text):
        import pygame
        tts = edge_tts.Communicate(text, voice=self.voice)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            temp_file = f.name
        await tts.save(temp_file)
        pygame.mixer.init()
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.quit()
        os.unlink(temp_file)

    def speak(self, text):
        """Speak the given text using ElevenLabs or Edge TTS"""
        print(f"\n🔊 ZORO: {text}\n")
        if self.use_elevenlabs and self.elevenlabs_api_key:
            try:
                from elevenlabs.client import ElevenLabs
                from elevenlabs import play
                client = ElevenLabs(api_key=self.elevenlabs_api_key)
                from elevenlabs import play
                audio = client.text_to_speech.convert(
                text=text,
                voice_id="21m00Tcm4TlvDq8ikWAM",
                 model_id="eleven_monolingual_v1"
            )
                play(audio)
            except Exception as e:
                print(f"ElevenLabs error: {e} — falling back to Edge TTS")
                asyncio.run(self._speak_edge(text))
        else:
            asyncio.run(self._speak_edge(text))
