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


def test_vehicle_status_exposes_simulator_as_disconnected():
    response = client.get("/api/vehicle/status")
    assert response.status_code == 200
    assert response.json()["connected"] is False
    assert response.json()["stale"] is True


def test_vehicle_discovery_is_noninvasive():
    response = client.get("/api/vehicle/discover")
    assert response.status_code == 200
    assert response.json()["ports"] == []
    assert "no vehicle commands were sent" in response.json()["message"]


def test_voice_status_discloses_browser_dependencies_and_no_autostart():
    response = client.get("/api/voice/status")
    assert response.status_code == 200
    data = response.json()
    assert data["microphone_autostart"] is False
    assert data["requires_user_gesture"] is True
    assert any("remotely" in item for item in data["limitations"])


def test_dashboard_exposes_manual_and_wake_phrase_voice_controls():
    response = client.get("/")
    assert response.status_code == 200
    assert "Push to talk" in response.text
    assert "Hey Autobot" in response.text
    assert "speechSynthesis" in response.text
