import asyncio
import sys
from types import SimpleNamespace


from autobot.vehicle.obd import OBDAdapter

class FakeValue:
    def __init__(self, value):
        self.magnitude = value
    def to(self, _unit):
        return self

class FakeResponse:
    def __init__(self, value):
        self.value = FakeValue(value)
    def is_null(self):
        return self.value.magnitude is None

class FakeConnection:
    def __init__(self, **_kwargs):
        self.connected = True
        self.queries = []
    def is_connected(self):
        return self.connected
    def query(self, command):
        self.queries.append(command)
        values = {"RPM": 850, "SPEED": 0, "COOLANT_TEMP": 91, "FUEL_LEVEL": 63}
        return FakeResponse(values[command])
    def close(self):
        self.connected = False

def test_obd_reads_only_supported_standard_sensor_pids(monkeypatch):
    commands = SimpleNamespace(RPM="RPM", SPEED="SPEED", COOLANT_TEMP="COOLANT_TEMP",
                               FUEL_LEVEL="FUEL_LEVEL")
    monkeypatch.setitem(sys.modules, "obd", SimpleNamespace(commands=commands))
    fake = FakeConnection()
    adapter = OBDAdapter(port="/dev/ttyUSB0", connection_factory=lambda **kwargs: fake,
                         serial_scanner=lambda: ["/dev/ttyUSB0"], poll_interval=0.5)
    snapshot = asyncio.run(adapter.snapshot())
    assert snapshot.connected is True
    assert snapshot.stale is False
    assert snapshot.values == {"rpm": 850.0, "speed_kph": 0.0,
                               "coolant_c": 91.0, "fuel_percent": 63.0}
    assert fake.queries == ["RPM", "SPEED", "COOLANT_TEMP", "FUEL_LEVEL"]
    asyncio.run(adapter.close())

def test_discovery_reports_candidate_ports_without_connecting():
    adapter = OBDAdapter(serial_scanner=lambda: ["/dev/ttyUSB0"],
                         connection_factory=lambda **kwargs: None)
    assert asyncio.run(adapter.discover()) == ["/dev/ttyUSB0"]
    assert adapter._connection is None

def test_missing_dependency_is_reported_as_unavailable(monkeypatch):
    import builtins
    original_import = builtins.__import__
    def blocked(name, *args, **kwargs):
        if name == "obd":
            raise ImportError("not installed")
        return original_import(name, *args, **kwargs)
    monkeypatch.setattr(builtins, "__import__", blocked)
    adapter = OBDAdapter()
    assert asyncio.run(adapter.discover()) == []
def test_polling_interval_prevents_repeated_pid_queries(monkeypatch):
    commands = SimpleNamespace(RPM="RPM", SPEED="SPEED", COOLANT_TEMP="COOLANT_TEMP",
                               FUEL_LEVEL="FUEL_LEVEL")
    monkeypatch.setitem(sys.modules, "obd", SimpleNamespace(commands=commands))
    fake = FakeConnection()
    adapter = OBDAdapter(connection_factory=lambda **kwargs: fake,
                         serial_scanner=list, poll_interval=2.0)
    asyncio.run(adapter.snapshot())
    first_count = len(fake.queries)
    asyncio.run(adapter.snapshot())
    assert first_count == 4
    assert len(fake.queries) == first_count
    asyncio.run(adapter.close())
