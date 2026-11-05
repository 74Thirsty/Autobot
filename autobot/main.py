from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from autobot.api.schemas import ChatRequest, ChatResponse
from autobot.config import get_settings
from autobot.core.assistant import Assistant
from autobot.intelligence.stub import StubProvider
from autobot.memory.store import MemoryStore
from autobot.vehicle.simulator import SimulatorAdapter
from autobot.vehicle.obd import OBDAdapter

settings = get_settings()
memory = MemoryStore(settings.database_file)
provider = StubProvider()
assistant = Assistant(provider, memory)
vehicle = (OBDAdapter(port=settings.obd_port, poll_interval=settings.obd_poll_interval, stale_after=settings.obd_stale_after, timeout=settings.obd_timeout) if settings.obd_adapter.lower() == "obd" else SimulatorAdapter())
@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await vehicle.close()

app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

@app.get("/", response_class=HTMLResponse)
async def dashboard() -> str:
    return '''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Autobot</title>
<style>:root{color-scheme:dark;font-family:system-ui}body{margin:0;background:#101820;color:#eef4f7}
main{max-width:850px;margin:8vh auto;padding:24px}h1{font-size:2.6rem;margin-bottom:0}
.sub{color:#a9bbc5}.card{background:#1b2a34;border:1px solid #314652;border-radius:14px;padding:20px;margin:18px 0}
button{background:#36a2a0;color:#06191a;border:0;border-radius:8px;padding:12px 18px;font-weight:700}
input{box-sizing:border-box;width:100%;padding:14px;border-radius:8px;border:1px solid #49616d;background:#101820;color:white}
#reply{white-space:pre-wrap;line-height:1.5}.tag{color:#9bd9bd}</style></head><body><main>
<h1>Autobot</h1><p class="sub">Vehicle AI assistant · local scaffold</p>
<section class="card"><h2>System</h2><p class="tag">● API online</p>
<p>AI: local stub · Vehicle: simulator · Voice: not configured</p>
<p class="sub">Simulated values are not live vehicle telemetry.</p></section>
<section class="card"><h2>Talk to Autobot</h2><form id="chat"><input id="message" maxlength="4000"
placeholder="Ask Autobot something…" required><p><button>Send message</button></p></form><div id="reply"></div></section>
<script>document.querySelector('#chat').addEventListener('submit',async e=>{e.preventDefault();
const box=document.querySelector('#reply');box.textContent='Thinking…';try{const r=await fetch('/api/chat',
{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:document.querySelector('#message').value})});
const d=await r.json();box.textContent=d.reply||d.detail||'Request failed';}catch(err){box.textContent=String(err)}})</script>
</main></body></html>'''

@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok", "app": settings.app_name, "environment": settings.app_env}

@app.get("/api/status")
async def status() -> dict:
    snapshot = await vehicle.snapshot()
    return {"application": "online", "ai_provider": provider.name,
            "vehicle": {"connected": snapshot.connected, "adapter": snapshot.adapter,
                        "vehicle": snapshot.vehicle, "values": snapshot.values,
                        "message": snapshot.message, "updated_at": snapshot.updated_at,
                        "age_seconds": snapshot.age_seconds, "stale": snapshot.stale,
                        "errors": snapshot.errors},
            "voice": {"input": settings.voice_input, "output": settings.voice_output}}

@app.get("/api/vehicle/status")
async def vehicle_status() -> dict:
    snapshot = await vehicle.snapshot()
    return {"connected": snapshot.connected, "adapter": snapshot.adapter,
            "vehicle": snapshot.vehicle, "values": snapshot.values,
            "message": snapshot.message, "updated_at": snapshot.updated_at,
            "age_seconds": snapshot.age_seconds, "stale": snapshot.stale,
            "errors": snapshot.errors}

@app.get("/api/vehicle/discover")
async def vehicle_discover() -> dict:
    ports = await vehicle.discover()
    return {"adapter": vehicle.name, "ports": ports,
            "message": "Serial discovery only; no vehicle commands were sent."}

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
