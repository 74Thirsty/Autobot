from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

@dataclass
class VehicleSnapshot:
    connected: bool
    adapter: str
    vehicle: str | None
    values: dict[str, Any]
    message: str
    updated_at: str | None = None
    age_seconds: float | None = None
    stale: bool = True
    errors: dict[str, str | None] = field(default_factory=dict)

class VehicleAdapter(ABC):
    name = "base"
    @abstractmethod
    async def snapshot(self) -> VehicleSnapshot:
        """Return a read-only snapshot of available vehicle data."""
        raise NotImplementedError

    async def close(self) -> None:
        """Release hardware resources, if any."""
