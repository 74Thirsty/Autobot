from autobot.intelligence.base import AIProvider


class StubProvider(AIProvider):
    """Credential-free provider used for local development."""
    name = "stub"
    async def generate(self, prompt: str) -> str:
        return ("Autobot is running in local scaffold mode. No AI model is connected yet. "
                f"I received: {prompt[:500]}")
