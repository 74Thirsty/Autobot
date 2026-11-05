from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from autobot.api.schemas import ChatRequest, ChatResponse
from autobot.config import get_settings
from autobot.core.assistant import Assistant
from autobot.intelligence.stub import StubProvider
from autobot.memory.store import MemoryStore
from autobot.vehicle.obd import OBDAdapter
from autobot.vehicle.simulator import SimulatorAdapter

settings = get_settings()
memory = MemoryStore(settings.database_file)
provider = StubProvider()
assistant = Assistant(provider, memory)
vehicle = (
    OBDAdapter(
        port=settings.obd_port,
        poll_interval=settings.obd_poll_interval,
        stale_after=settings.obd_stale_after,
        timeout=settings.obd_timeout,
    )
    if settings.obd_adapter.lower() == "obd"
    else SimulatorAdapter()
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await vehicle.close()


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)


@app.get("/", response_class=HTMLResponse)
async def dashboard() -> str:
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#101820"><title>Autobot</title>
<style>
:root{color-scheme:dark;font-family:system-ui,sans-serif}*{box-sizing:border-box}
body{margin:0;background:#101820;color:#eef4f7}main{max-width:900px;margin:0 auto;padding:clamp(16px,4vw,36px)}
h1{font-size:clamp(2.2rem,7vw,3.2rem);margin:0}.sub{color:#a9bbc5}
.card{background:#1b2a34;border:1px solid #314652;border-radius:16px;padding:clamp(16px,3vw,24px);margin:18px 0}
button,input{font:inherit;border-radius:10px}button{background:#36a2a0;color:#06191a;border:0;padding:12px 18px;font-weight:700;cursor:pointer}
button.secondary{background:#314652;color:#eef4f7}button:disabled{opacity:.45;cursor:not-allowed}
input{width:100%;padding:14px;border:1px solid #49616d;background:#101820;color:white}
.controls{display:flex;gap:10px;flex-wrap:wrap;margin:12px 0}.controls button{flex:1;min-width:145px}
#reply{white-space:pre-wrap;line-height:1.55;min-height:24px}.tag{color:#9bd9bd}
.status{font-size:.95rem;color:#b8cbd4}.notice{font-size:.88rem;color:#a9bbc5;line-height:1.5}
#transcript{color:#b8cbd4;min-height:1.3em}.brand{display:flex;justify-content:space-between;align-items:end;gap:16px;flex-wrap:wrap}
</style></head><body><main>
<header class="brand"><div><h1>Autobot</h1><p class="sub">Your vehicle companion · Raspberry Pi</p></div>
<p class="tag">● Local dashboard online</p></header>
<section class="card"><h2>Vehicle</h2><p id="vehicle-status" class="status">Checking adapter…</p>
<p class="notice">Vehicle telemetry is read-only. Do not interact with this screen while driving.</p></section>
<section class="card"><h2>Talk to Autobot</h2>
<form id="chat"><input id="message" maxlength="4000" autocomplete="off" placeholder="Type a message…" required>
<div class="controls"><button id="send" type="submit">Send</button></div></form>
<div class="controls"><button id="push" type="button">🎙 Push to talk</button>
<button id="wake" class="secondary" type="button">Enable “Hey Autobot”</button>
<button id="voice" class="secondary" type="button" aria-pressed="true">🔊 Voice on</button></div>
<p id="voice-status" class="status" aria-live="polite">Voice is off until you enable it.</p>
<p id="transcript"></p><div id="reply" aria-live="polite"></div>
<p class="notice">Microphone access starts only after you press a voice button. Wake-phrase mode keeps browser speech recognition active until stopped. Browser speech recognition may send audio to your browser vendor for transcription; browser speech synthesis handles spoken replies. Use HTTPS (or localhost). Push-to-talk is the manual fallback.</p>
</section>
<script>
const $=s=>document.querySelector(s), SpeechRecognition=window.SpeechRecognition||window.webkitSpeechRecognition;
let recognition=null, mode='off', speaking=true, busy=false;
function voiceMessage(t){$('#voice-status').textContent=t}
function stopRecognition(){if(recognition){try{recognition.stop()}catch(e){} recognition=null}mode='off';$('#wake').textContent='Enable “Hey Autobot”'}
async function askAutobot(text){
 const clean=text.trim();if(!clean||busy)return;busy=true;$('#message').value=clean;$('#transcript').textContent='You: '+clean;$('#reply').textContent='Autobot is thinking…';
 try{const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:clean})});
 const d=await r.json();if(!r.ok)throw Error(d.detail||'Request failed');$('#reply').textContent=d.reply;
 if(speaking&&window.speechSynthesis){window.speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(d.reply);window.speechSynthesis.speak(u)}
 }catch(e){$('#reply').textContent='Unable to reach Autobot: '+e.message}finally{busy=false;if(mode==='wake'&&!recognition)setTimeout(()=>{if(mode==='wake'&&!recognition)startRecognition('wake')},400)}
}
function startRecognition(kind){
 if(!SpeechRecognition){voiceMessage('Speech recognition is not supported by this browser. Use text chat or a supported Chromium browser.');return}
 stopRecognition();const r=new SpeechRecognition();recognition=r;mode=kind;r.lang=navigator.language||'en-US';r.continuous=kind==='wake';r.interimResults=false;r.maxAlternatives=1;
 r.onstart=()=>voiceMessage(kind==='wake'?'Listening for “Hey Autobot”…':'Listening… speak now.');
 r.onerror=e=>{voiceMessage('Microphone/speech error: '+e.error+'. Check browser permission and microphone.');if(kind==='push')stopRecognition()};
 r.onresult=e=>{for(let i=e.resultIndex;i<e.results.length;i++){if(!e.results[i].isFinal)continue;
 const words=e.results[i][0].transcript.trim();if(kind==='push'){stopRecognition();askAutobot(words);return}
 const match=words.match(/\\bhey\\s+autobot\\b[,.!\\s]*(.*)/i);if(match){const command=match[1].trim();if(command){askAutobot(command)}else{voiceMessage('I’m listening. Say your request.');startRecognition('push');return}}
 }};
 r.onend=()=>{if(recognition===r)recognition=null;if(kind==='wake'&&mode==='wake'){if(!busy)setTimeout(()=>{if(mode==='wake'&&!recognition)startRecognition('wake')},350)}else if(kind==='push'){mode='off';voiceMessage('Voice capture ended.')}};
 try{r.start()}catch(e){recognition=null;mode='off';voiceMessage('Could not start microphone: '+e.message)}
}
$('#chat').addEventListener('submit',e=>{e.preventDefault();askAutobot($('#message').value)});
$('#push').addEventListener('click',()=>{if(mode!=='off')stopRecognition();startRecognition('push')});
$('#wake').addEventListener('click',()=>{if(mode==='wake'){stopRecognition();voiceMessage('Wake-phrase listening stopped.')}else{startRecognition('wake')}});
$('#voice').addEventListener('click',()=>{speaking=!speaking;$('#voice').textContent=speaking?'🔊 Voice on':'🔇 Voice off';$('#voice').setAttribute('aria-pressed',String(speaking));if(!speaking&&window.speechSynthesis)window.speechSynthesis.cancel()});
window.addEventListener('pagehide',()=>{stopRecognition();if(window.speechSynthesis)window.speechSynthesis.cancel()});
fetch('/api/status').then(r=>r.json()).then(d=>{const v=d.vehicle;$('#vehicle-status').textContent='Vehicle: '+(v.connected?'connected':'not connected')+' · '+v.adapter+' · '+v.message}).catch(()=>{$('#vehicle-status').textContent='Vehicle status unavailable'});
</script></main></body></html>"""


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok", "app": settings.app_name, "environment": settings.app_env}


@app.get("/api/status")
async def status() -> dict:
    snapshot = await vehicle.snapshot()
    return {
        "application": "online",
        "ai_provider": provider.name,
        "vehicle": {
            "connected": snapshot.connected,
            "adapter": snapshot.adapter,
            "vehicle": snapshot.vehicle,
            "values": snapshot.values,
            "message": snapshot.message,
            "updated_at": snapshot.updated_at,
            "age_seconds": snapshot.age_seconds,
            "stale": snapshot.stale,
            "errors": snapshot.errors,
        },
        "voice": {"input": "browser", "output": "browser", "wake_phrase": "browser-speech"},
    }


@app.get("/api/voice/status")
async def voice_status() -> dict:
    return {
        "input": "browser Web Speech API",
        "output": "browser SpeechSynthesis API",
        "wake_phrase": "Hey Autobot",
        "microphone_autostart": False,
        "requires_user_gesture": True,
        "limitations": [
            "Speech recognition availability and offline behavior depend on the browser.",
            "The browser speech recognition provider may process audio remotely.",
            "Wake-phrase mode is active only while the dashboard remains open.",
        ],
    }


@app.get("/api/vehicle/status")
async def vehicle_status() -> dict:
    snapshot = await vehicle.snapshot()
    return {
        "connected": snapshot.connected,
        "adapter": snapshot.adapter,
        "vehicle": snapshot.vehicle,
        "values": snapshot.values,
        "message": snapshot.message,
        "updated_at": snapshot.updated_at,
        "age_seconds": snapshot.age_seconds,
        "stale": snapshot.stale,
        "errors": snapshot.errors,
    }


@app.get("/api/vehicle/discover")
async def vehicle_discover() -> dict:
    ports = await vehicle.discover()
    return {
        "adapter": vehicle.name,
        "ports": ports,
        "message": "Serial discovery only; no vehicle commands were sent.",
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    try:
        reply = await assistant.respond(request.message, request.session_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return ChatResponse(reply=reply, session_id=request.session_id)


@app.get("/api/memory/{session_id}")
async def conversation(session_id: str) -> dict:
    return {"session_id": session_id, "messages": memory.recent_messages(session_id)}
