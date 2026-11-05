# Autobot

**An AI companion and vehicle-information platform for a 2011 Lincoln MKT, designed for Raspberry Pi 5.**

Autobot is a modular hybrid vehicle assistant. The Raspberry Pi is the in-car edge computer; optional cloud AI services provide richer conversation and research capabilities. Hardware, voice, AI providers, memory, and vehicle integrations evolve independently.

## Status

The application scaffold, Phase 2 read-only OBD-II software integration, and Phase 3 browser-based voice/touchscreen interface are implemented. Automated test execution, physical OBD adapter validation, and Raspberry Pi microphone/speaker/browser validation remain outstanding. Browser speech recognition may depend on an external speech service; offline voice operation is not yet provided.

## Principles

- Local-first core; no cloud credentials required to start.
- Pluggable AI providers and hardware adapters.
- Graceful degradation when internet or providers are unavailable.
- Conversations and telemetry remain local unless a configured provider is deliberately used.
- Vehicle integration is **read-only OBD-II**. No actuator, steering, braking, throttle, transmission, or arbitrary CAN-write capability.
- Simulated data must never be represented as live vehicle data.
- Microphone access requires an explicit user action; voice is not automatically activated.

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
  main.py          Application entry point and browser dashboard
tests/              API and safety-boundary tests
docs/               Architecture, OBD-II, voice, and roadmap
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

For microphone, speech recognition, push-to-talk, and “Hey Autobot” setup, see [the voice guide](docs/VOICE.md). Browser speech recognition support varies and may require a network speech service.

## Vehicle target

The initial target vehicle is a **2011 Lincoln MKT**. The Pi 5 runs the local API, dashboard, memory, orchestration, and device adapters. Cloud AI is optional. Start hardware integration with an ELM327-compatible adapter in read-only diagnostic mode.

Raspberry Pi 5 has USB, Bluetooth, Wi-Fi, GPIO, camera/display interfaces, and PCIe. See the official [Raspberry Pi documentation](https://www.raspberrypi.com/documentation/). Use an automotive-rated 12V-to-5V supply with transient protection; never connect the Pi directly to vehicle power. Confirm the exact hardware and power design before installation.

## Roadmap

1. [x] Modular Python scaffold and runnable API
2. [x] Local SQLite conversation persistence
3. [x] Simulated read-only vehicle adapter
4. [x] ELM327 discovery, read-only PID polling, and stale-data reporting (hardware validation pending)
5. [x] Browser-based push-to-talk, wake-phrase mode, speech input/output, and responsive dashboard (Pi validation pending)
6. [ ] Verify clean install, tests, and CI
7. [ ] Physically validate OBD-II adapter against the Lincoln MKT
8. [ ] Native/offline voice engine and dedicated wake-word detector
9. [ ] Configurable cloud/local model providers
10. [ ] Validate ignition, sleep, shutdown, brownout, and reconnect behavior in vehicle

## Safety and privacy

Autobot is informational, not safety-critical. The driver remains responsible for driving; do not interact with the dashboard while driving. Vehicle data may be delayed or unavailable. Browser speech recognition may transmit audio to a browser vendor's recognition service. Keep credentials in environment variables; never commit secrets, vehicle identifiers, or personal data.
