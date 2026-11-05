# Roadmap

## Phase 0 — Scaffold
- [x] Modular Python package and configuration
- [x] FastAPI dashboard and API
- [x] SQLite message persistence
- [x] AI provider abstraction and local stub
- [x] Read-only vehicle adapter contract and disconnected simulator
- [ ] Clean-environment tests and CI verification

## Phase 1 — Local device foundation
- [ ] Raspberry Pi OS 64-bit install guide and systemd service
- [ ] Structured rotating logs and diagnostics endpoint
- [ ] Hardware inventory and device health reporting
- [ ] Graceful shutdown and startup recovery

## Phase 2 — Vehicle data
- [x] ELM327 serial adapter discovery and connection lifecycle (implementation; hardware validation pending)
- [x] Read-only OBD-II PID polling with configurable rate limits
- [x] Data freshness, stale readings, and unavailable-state handling
- [ ] Physically validate against 2011 Lincoln MKT without modifying vehicle systems

## Phase 3 — Voice and interface
- [x] Browser microphone/speaker path using Web Speech APIs (browser-dependent)
- [x] Push-to-talk speech capture
- [x] Optional “Hey Autobot” wake-phrase mode while dashboard is open
- [x] Browser speech-to-text and speech output
- [x] Responsive touchscreen-friendly dashboard
- [ ] Validate microphone, speaker, browser support, and wake-phrase reliability on Raspberry Pi 5
- [ ] Native/offline wake-word and speech engines (not included in browser implementation)

## Phase 4 — Intelligence and memory
- [ ] Configurable cloud provider adapter
- [ ] Optional local model adapter
- [ ] Retrieval over user-approved local notes
- [ ] Explicit retention, deletion, and export controls

## Phase 5 — Vehicle deployment
- [ ] Automotive-rated power management
- [ ] Ignition-aware startup/shutdown behavior
- [ ] Offline and reconnect testing
- [ ] Thermal, vibration, and long-duration testing
