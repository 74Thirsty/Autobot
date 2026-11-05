from abc import ABC, abstractmethod


class AIProvider(ABC):
    name = "base"
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        raise NotImplementedError
