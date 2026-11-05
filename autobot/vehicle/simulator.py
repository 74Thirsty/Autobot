from autobot.vehicle.base import VehicleAdapter, VehicleSnapshot


class SimulatorAdapter(VehicleAdapter):
    """Simulated data; never claims a physical vehicle is connected."""
    name = "simulator"

    async def snapshot(self) -> VehicleSnapshot:
        return VehicleSnapshot(
            connected=False,
            adapter=self.name,
            vehicle="2011 Lincoln MKT (configured target; not verified)",
            values={"rpm": None, "speed_kph": None, "coolant_c": None, "fuel_percent": None},
            message="Simulator selected. No OBD-II adapter or live vehicle data detected.",
            stale=True,
            errors={},
        )

    async def discover(self) -> list[str]:
        return []
