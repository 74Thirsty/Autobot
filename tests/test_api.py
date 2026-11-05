from fastapi.testclient import TestClient
from autobot.main import app

client = TestClient(app)

def test_health() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_status_does_not_claim_vehicle_connection() -> None:
    response = client.get("/api/status")
    assert response.status_code == 200
    assert response.json()["vehicle"]["connected"] is False

def test_chat_and_local_memory() -> None:
    response = client.post("/api/chat", json={"message": "Hello", "session_id": "test-session"})
    assert response.status_code == 200
    assert "local scaffold mode" in response.json()["reply"]
    history = client.get("/api/memory/test-session")
    assert [m["role"] for m in history.json()["messages"]] == ["user", "assistant"]
