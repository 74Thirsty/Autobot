# Voice and touchscreen setup

## What Phase 3 provides

The dashboard now uses the browser's built-in speech interfaces:
- **Push to talk:** press the microphone button, speak one request, and the transcript is sent to `POST /api/chat`.
- **Wake phrase:** explicitly enable “Hey Autobot”; the browser keeps speech recognition active while the dashboard is open and waits for that phrase.
- **Speech output:** replies are spoken with the browser's SpeechSynthesis API. The voice toggle mutes/unmutes spoken replies.
- **Touchscreen:** the dashboard layout and controls resize for touch displays and mobile-sized screens.

No microphone is opened automatically. The user must press a voice control and grant browser permission.

## Requirements and limitations

Use a browser that implements `SpeechRecognition` (commonly available in Chromium-based browsers, but support varies) and `SpeechSynthesis`. Serve the dashboard from HTTPS or localhost so microphone permission is available. Select the Raspberry Pi microphone and speaker in the operating system/browser audio settings.

**Privacy:** browser speech recognition behavior depends on the browser and its configured recognition service. Audio may be sent to the browser vendor or its speech service for transcription. This implementation does not claim offline speech recognition. Speech synthesis is provided by the browser and available system voices.

**Wake phrase:** “Hey Autobot” is phrase detection over browser speech recognition, not a dedicated low-power always-on wake-word engine. It runs only while the dashboard is open, consumes microphone/browser resources, and may be unreliable in vehicle noise. It is not a production automotive hands-free system.

## Use

1. Start Autobot and open the dashboard from the Pi or a device on the same trusted network.
2. Confirm the browser has access to the intended microphone.
3. Press **Push to talk**, speak, and wait for the response.
4. Or explicitly enable **Hey Autobot** to keep recognition active until stopped.
5. Use **Voice on/off** to control spoken replies. Text replies remain visible.

If speech recognition is unavailable, use the text chat. No audio is captured by the backend API; the browser submits recognized text to the existing chat endpoint.

## Next hardware validation

- Verify microphone input and speaker output on the actual Pi 5.
- Verify Chromium speech-recognition support in the installed OS/browser build.
- Test push-to-talk in a quiet room and with realistic cabin noise.
- Measure wake-phrase false activations, missed activations, CPU use, and reconnect behavior.
- Decide whether to replace browser recognition with an offline engine and dedicated wake-word detector before unattended in-car use.
