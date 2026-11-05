from abc import ABC, abstractmethod


class SpeechInput(ABC):
    @abstractmethod
    async def listen(self) -> str:
        raise NotImplementedError

class SpeechOutput(ABC):
    @abstractmethod
    async def speak(self, text: str) -> None:
        raise NotImplementedError
