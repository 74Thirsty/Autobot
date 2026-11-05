from autobot.intelligence.base import AIProvider
from autobot.memory.store import MemoryStore

class Assistant:
    """Coordinates user messages, model responses, and local conversation history."""
    def __init__(self, provider: AIProvider, memory: MemoryStore) -> None:
        self.provider = provider
        self.memory = memory

    async def respond(self, message: str, session_id: str = "default") -> str:
        clean_message = message.strip()
        if not clean_message:
            raise ValueError("Message cannot be empty")
        self.memory.add_message(session_id, "user", clean_message)
        reply = await self.provider.generate(clean_message)
        self.memory.add_message(session_id, "assistant", reply)
        return reply
