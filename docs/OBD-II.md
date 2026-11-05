# OBD-II adapter setup and validation

## Supported first-pass data

Autobot queries only standard read-only OBD-II sensor commands:

| API field | PID command | Unit |
| --- | --- | --- |
| rpm | RPM | revolutions/minute |
| speed_kph | SPEED | km/h |
| coolant_c | COOLANT_TEMP | °C |
| fuel_percent | FUEL_LEVEL | % |

A PID may be unsupported by a particular ECU or adapter. Unsupported/no-response values remain null with per-PID error details. Zero speed or RPM is a valid reading.

## Install

Install the optional adapter dependency:

```bash
pip install -e ".[vehicle,dev]"
```

Set in `.env`:

```dotenv
OBD_ADAPTER=obd
OBD_PORT=
OBD_POLL_INTERVAL=2.0
OBD_STALE_AFTER=8.0
OBD_TIMEOUT=2.0
```

An empty `OBD_PORT` lets python-OBD select a serial adapter. Set an explicit path such as `/dev/ttyUSB0` or `/dev/rfcomm0` if needed. Linux serial permissions may require adding the service user to the appropriate device-access group.

## Discovery and status

- `GET /api/vehicle/discover` lists candidate serial ports; it does not open a connection or send commands.
- `GET /api/status` returns system status and the latest vehicle snapshot.
- `GET /api/vehicle/status` returns the vehicle snapshot directly.

The response includes connection state, last successful sample timestamp, sample age, stale flag, values, and per-PID errors. Last-known values are retained when a later poll fails, but are marked stale and must not be treated as current.

## Physical validation checklist

1. Park safely, select Park, apply the parking brake, and keep the engine off for initial adapter discovery.
2. Connect a known ELM327-compatible adapter to the diagnostic connector. Do not probe or modify vehicle wiring.
3. Confirm candidate port discovery; set `OBD_PORT` explicitly if required.
4. Start the engine only while safely parked and confirm the adapter reports a vehicle connection.
5. Check plausible RPM, speed (0 while stationary), coolant temperature, and fuel level. Compare with the instrument cluster where appropriate.
6. Confirm unsupported PIDs remain null. Disconnect the adapter and verify values become stale/unavailable rather than fabricated.
7. Repeat after reconnect and an ignition cycle.

The initial PID set does not electronically verify make/model. The configured target is a 2011 Lincoln MKT; compatibility still requires physical confirmation.

## Safety boundary

Only the four standard sensor queries above are issued. No clear/reset commands, actuator tests, coding, adaptations, manufacturer-specific commands, or arbitrary CAN frames are implemented. Do not operate the dashboard while driving.
