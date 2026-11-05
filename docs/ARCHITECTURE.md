# Autobot architecture

## Runtime boundaries
- **API/UI:** FastAPI serves a local browser dashboard and JSON endpoints.
- **Core:** coordinates user messages, model responses, and local conversation history.
- **Intelligence:** provider interface. The initial stub keeps development credential-free.
- **Memory:** local SQLite persistence.
- **Vehicle:** adapter interface. The simulator is explicitly disconnected. ELM327 integration exposes read-only OBD-II operations only.
- **Voice/UI:** browser Web Speech APIs provide user-initiated speech recognition and speech synthesis. The dashboard offers push-to-talk and an optional wake phrase while the page is open. Browser support and speech-recognition privacy/offline behavior vary.

## Deployment topology
Raspberry Pi 5 runs the local API, dashboard, SQLite store, device adapters, and lightweight orchestration. Cloud AI is optional. Browser voice recognition may use a remote browser-vendor speech service and is not guaranteed to work offline.

## Voice privacy and lifecycle
The microphone is not opened on page load. A user must explicitly start push-to-talk or wake-phrase mode and grant browser permission. Wake-phrase mode remains active only while the dashboard is open and can be stopped by the user. The browser submits recognized text to the API; the backend does not receive raw audio in this phase.

## Vehicle safety boundary
The first vehicle integration is diagnostic/read-only. Do not implement arbitrary CAN transmission or control of vehicle actuators. Any future expansion requires a separate safety review and must not interfere with factory vehicle systems.

## Data handling
Conversation history is stored on-device. Provider adapters must disclose when prompts leave the device. Secrets are environment variables and must never be committed. Logs must avoid API keys, tokens, and unnecessary personal data.
