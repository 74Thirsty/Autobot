# Autobot

**An AI companion and vehicle-information platform for a 2011 Lincoln MKT, designed for Raspberry Pi 5.**

Autobot is a modular hybrid vehicle assistant. The Raspberry Pi is the in-car edge computer; optional cloud AI services provide richer conversation and research capabilities. Hardware, voice, AI providers, memory, and vehicle integrations evolve independently.

## Status

The initial application scaffold and Phase 2 read-only OBD-II software integration are implemented. Physical adapter compatibility and live readings still require validation on the target vehicle. Microphone/speaker, Bluetooth routing, and cloud model integrations remain future work.

## Principles

- Local-first core; no cloud credentials required to start.
- Pluggable AI providers and hardware adapters.
- Graceful degradation when internet or providers are unavailable.
- Conversations and telemetry remain local unless a configured provider is deliberately used.
- Vehicle integration is **read-only OBD-II**. No actuator, steering, braking, throttle, transmission, or arbitrary CAN-write capability.
- Simulated data must never be represented as live vehicle data.

## Architecture

```text
autobot/
  api/             FastAPI routes and schemas
  core/            Application lifecycle and orchestration
  intelligence/    Provider interface and local stub
  memory/          SQLite conversation/event store
  vehicle/         Read-only OBD-II interface and simulator
  voice/           Speech input/output interfaces
  config.py        Environment-backed settings
  main.py          Application entry point
tests/             API and safety-boundary tests
docs/              Architecture and roadmap
```

## Quick start

Python 3.11+:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn autobot.main:app --host 0.0.0.0 --port 8000 --reload
```

Dashboard: http://localhost:8000 · API docs: http://localhost:8000/docs

Run checks: `ruff check . && pytest`

For physical ELM327/OBD-II integration, install `pip install -e ".[vehicle,dev]"`, set `OBD_ADAPTER=obd` in `.env`, and follow [the OBD-II setup and safety validation guide](docs/OBD-II.md).

## Vehicle target

The initial target vehicle is a **2011 Lincoln MKT**. The Pi 5 runs the local API, dashboard, memory, orchestration, and device adapters. Cloud AI is optional. Start hardware integration with an ELM327-compatible adapter in read-only diagnostic mode.

Raspberry Pi 5 has USB, Bluetooth, Wi-Fi, GPIO, camera/display interfaces, and PCIe. See the official [Raspberry Pi documentation](https://www.raspberrypi.com/documentation/). Use an automotive-rated 12V-to-5V supply with transient protection; never connect the Pi directly to vehicle power. Confirm the exact hardware and power design before installation.

## Roadmap

1. [x] Modular Python scaffold and runnable API
2. [x] Local SQLite conversation persistence
3. [x] Simulated read-only vehicle adapter
4. [x] ELM327 discovery, read-only PID polling, and stale-data reporting (hardware validation pending)
5. [ ] Verify clean install, tests, and CI
6. [ ] Physically validate OBD-II adapter against the Lincoln MKT
7. [ ] Add voice capture and speech output
8. [ ] Add configurable cloud/local model providers
9. [ ] Build touchscreen dashboard and startup/service packaging
10. [ ] Validate ignition, sleep, shutdown, brownout, and reconnect behavior in vehicle

## Safety and privacy

Autobot is informational, not safety-critical. The driver remains responsible for driving; do not interact with the dashboard while driving. Vehicle data may be delayed or unavailable. Keep credentials in environment variables; never commit secrets, vehicle identifiers, or personal data.