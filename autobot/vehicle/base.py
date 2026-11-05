from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

@dataclass
class VehicleSnapshot:
    connected: bool
    adapter: str
    vehicle: str | None
    values: dict[str, Any]
    message: str

class VehicleAdapter(ABC):
    name = "base"
    @abstractmethod
    async def snapshot(self) -> VehicleSnapshot:
        """Return a read-only snapshot of available vehicle data."""
        raise NotImplementedError
