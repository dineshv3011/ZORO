import os
from dotenv import load_dotenv

load_dotenv()

class ZOROMemory:
    def __init__(self):
        self.api_key = os.getenv("HINDSIGHT_API_KEY")
        self.client = None
        self.local_memory = []  # Fallback if Hindsight unavailable
        self._setup()

    def _setup(self):
        """Connect to Hindsight memory"""
        try:
            from hindsight import HindsightClient
            self.client = HindsightClient(api_key=self.api_key)
            print("✅ Hindsight memory connected!")
        except Exception as e:
            print(f"⚠️ Hindsight not available, using local memory: {e}")

    def remember(self, info):
        """Save a memory to Hindsight"""
        try:
            if self.client:
                self.client.remember(info)
            else:
                self.local_memory.append(info)
            print(f"💾 Memory saved!")
        except Exception as e:
            self.local_memory.append(info)
            print(f"Memory saved locally: {e}")

    def recall(self, query):
        """Recall relevant memories for a query"""
        try:
            if self.client:
                result = self.client.recall(query)
                return str(result) if result else ""
            else:
                # Return last 10 local memories
                return "\n".join(self.local_memory[-10:])
        except Exception as e:
            print(f"Recall error: {e}")
            return "\n".join(self.local_memory[-10:])

    def remember_contact(self, name, email):
        """Remember a contact's email"""
        self.remember(f"Contact: {name} has email {email}")

    def remember_preference(self, preference):
        """Remember user preference"""
        self.remember(f"User preference: {preference}")

    def get_user_context(self):
        """Get full user context for AI personalization"""
        return self.recall("user preferences habits contacts schedule tasks")

    def get_contacts(self):
        """Get known contacts"""
        return self.recall("contacts email addresses")
