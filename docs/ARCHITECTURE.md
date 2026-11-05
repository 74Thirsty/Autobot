# Autobot architecture

## Runtime boundaries
- **API/UI:** FastAPI serves a local browser dashboard and JSON endpoints.
- **Core:** coordinates requests and stores messages; it does not know vendor-specific model APIs.
- **Intelligence:** provider interface. The initial stub keeps development credential-free.
- **Memory:** local SQLite persistence.
- **Vehicle:** adapter interface. The simulator is explicitly disconnected. Future ELM327 integration must expose read-only OBD-II operations only.
- **Voice:** speech input/output contracts. No microphone is opened until an implementation is selected and configured.

## Deployment topology
Raspberry Pi 5 runs the local API, dashboard, SQLite store, device adapters, and lightweight orchestration. Cloud AI is optional. Local functions must remain usable offline.

## Vehicle safety boundary
The first vehicle integration is diagnostic/read-only. Do not implement arbitrary CAN transmission or control of vehicle actuators. Any future expansion requires a separate safety review and must not interfere with factory vehicle systems.

## Data handling
Conversation history is stored on-device. Provider adapters must disclose when prompts leave the device. Secrets are environment variables and must never be committed. Logs must avoid API keys, tokens, and unnecessary personal data.
