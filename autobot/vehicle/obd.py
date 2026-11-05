"""Read-only ELM327 / OBD-II adapter using python-OBD.

This module never sends actuator or manufacturer-specific control commands.
Only standard diagnostic sensor PIDs are queried.
"""
import asyncio
import logging
import time
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from autobot.vehicle.base import VehicleAdapter, VehicleSnapshot

logger = logging.getLogger(__name__)

PID_COMMANDS = {
    "rpm": ("RPM", "rpm"),
    "speed_kph": ("SPEED", "km/h"),
    "coolant_c": ("COOLANT_TEMP", "degC"),
    "fuel_percent": ("FUEL_LEVEL", "percent"),
}


class OBDAdapter(VehicleAdapter):
    name = "obd"

    def __init__(
        self,
        port: str = "",
        poll_interval: float = 2.0,
        stale_after: float = 8.0,
        timeout: float = 2.0,
        connection_factory: Callable[..., Any] | None = None,
        serial_scanner: Callable[[], list[str]] | None = None,
    ) -> None:
        self.port = port.strip()
        self.poll_interval = max(0.5, poll_interval)
        self.stale_after = max(self.poll_interval, stale_after)
        self.timeout = max(0.5, timeout)
        self._connection_factory = connection_factory
        self._serial_scanner = serial_scanner
        self._connection: Any | None = None
        self._last_poll = 0.0
        self._last_success: float | None = None
        self._last_success_iso: str | None = None
        self._values: dict[str, float | None] = {key: None for key in PID_COMMANDS}
        self._pid_errors: dict[str, str | None] = {key: "not queried" for key in PID_COMMANDS}
        self._last_error: str | None = None
        self._lock = asyncio.Lock()

    def _dependencies(self) -> tuple[Any, Any]:
        if self._connection_factory and self._serial_scanner:
            return self._connection_factory, self._serial_scanner
        try:
            import obd
        except ImportError as exc:
            raise RuntimeError(
                "python-OBD is not installed. Install Autobot with: pip install -e '.[vehicle]'"
            ) from exc
        return self._connection_factory or obd.OBD, self._serial_scanner or obd.scan_serial

    async def discover(self) -> list[str]:
        """List candidate serial devices; discovery does not open or write to them."""
        try:
            _, scanner = self._dependencies()
            return await asyncio.to_thread(scanner)
        except (ImportError, OSError, RuntimeError, ValueError) as exc:
            self._last_error = str(exc)
            logger.warning("OBD serial discovery unavailable: %s", exc)
            return []

    def _ensure_connection(self) -> bool:
        factory, _ = self._dependencies()
        if self._connection is not None:
            try:
                if self._connection.is_connected():
                    return True
            except Exception:
                logger.debug("Existing OBD connection check failed", exc_info=True)
            self._close_connection()
        port = self.port or None
        self._connection = factory(portstr=port, fast=False, timeout=self.timeout)
        if not self._connection.is_connected():
            self._close_connection()
            self._last_error = "ELM327 adapter found, but no vehicle connection was established."
            return False
        self._last_error = None
        return True

    def _close_connection(self) -> None:
        if self._connection is not None:
            try:
                self._connection.close()
            except Exception:
                logger.debug("Ignoring error while closing OBD connection", exc_info=True)
        self._connection = None

    @staticmethod
    def _numeric_value(response: Any, target_unit: str) -> float | None:
        if response is None or response.is_null():
            return None
        value = response.value
        try:
            value = value.to(target_unit)
        except (AttributeError, ValueError, TypeError):
            pass
        magnitude = getattr(value, "magnitude", value)
        try:
            return round(float(magnitude), 2)
        except (TypeError, ValueError):
            return None

    def _poll_sync(self) -> None:
        self._last_poll = time.monotonic()
        if not self._ensure_connection():
            return
        try:
            import obd
            commands = obd.commands
            successful = 0
            for key, (command_name, unit) in PID_COMMANDS.items():
                command = getattr(commands, command_name, None)
                if command is None:
                    self._pid_errors[key] = "PID command unavailable in python-OBD"
                    continue
                try:
                    response = self._connection.query(command)
                    value = self._numeric_value(response, unit)
                    self._values[key] = value
                    self._pid_errors[key] = None if value is not None else "ECU returned no value"
                    successful += value is not None
                except (OSError, RuntimeError, ValueError, TypeError) as exc:
                    self._pid_errors[key] = str(exc)
                    logger.warning("OBD PID %s query failed: %s", key, exc)
            if successful:
                self._last_success = time.monotonic()
                self._last_success_iso = datetime.now(UTC).isoformat()
                self._last_error = None
            else:
                self._last_error = (
                    "Connected to adapter, but this poll returned no valid live PID values."
                )
        except Exception as exc:
            self._last_error = str(exc)
            logger.exception("OBD polling failed")
            self._close_connection()

    async def snapshot(self) -> VehicleSnapshot:
        async with self._lock:
            now = time.monotonic()
            if now - self._last_poll >= self.poll_interval:
                await asyncio.to_thread(self._poll_sync)
            now = time.monotonic()
            age = None if self._last_success is None else round(now - self._last_success, 2)
            connected = False
            if self._connection is not None:
                try:
                    connected = bool(self._connection.is_connected())
                except (OSError, RuntimeError):
                    connected = False
            stale = age is None or age > self.stale_after
            message = self._last_error or (
                "Live OBD-II data available." if connected and not stale
                else "OBD-II data is stale; showing last successful readings."
                if age is not None else
                "No live OBD-II readings available. Check adapter, cable, ignition state, and vehicle compatibility."
            )
            return VehicleSnapshot(
                connected=connected,
                adapter=self.name,
                vehicle="2011 Lincoln MKT (configured target; vehicle identity not electronically verified)",
                values=dict(self._values),
                message=message,
                updated_at=self._last_success_iso,
                age_seconds=age,
                stale=stale,
                errors=dict(self._pid_errors),
            )

    async def close(self) -> None:
        async with self._lock:
            await asyncio.to_thread(self._close_connection)
