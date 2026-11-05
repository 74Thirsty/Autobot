# Roadmap

## Phase 0 — Scaffold
- [x] Modular Python package and configuration
- [x] FastAPI dashboard and API
- [x] SQLite message persistence
- [x] AI provider abstraction and local stub
- [x] Read-only vehicle adapter contract and disconnected simulator
- [x] Voice input/output contracts
- [ ] Clean-environment tests and CI verification

## Phase 1 — Local device foundation
- [ ] Raspberry Pi OS 64-bit install guide and systemd service
- [ ] Structured rotating logs and diagnostics endpoint
- [ ] Hardware inventory and device health reporting
- [ ] Graceful shutdown and startup recovery

## Phase 2 — Vehicle data
- [ ] ELM327 adapter discovery and connection lifecycle
- [ ] Read-only OBD-II PID polling with rate limits
- [ ] Data freshness and unavailable-state handling
- [ ] Validate against 2011 Lincoln MKT without modifying vehicle systems

## Phase 3 — Voice and interface
- [ ] Select microphone and speaker path
- [ ] Wake-word and push-to-talk modes
- [ ] Speech-to-text and text-to-speech adapters
- [ ] Responsive touchscreen interface

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
