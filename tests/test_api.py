from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_set_command_returns_ok():
    response = client.post("/command", json={"command": "SET", "args": ["user:1", "Cuneyt"]})
    assert response.status_code == 200
    assert response.json() == {"ok": True, "result": "OK", "error": None}


def test_get_command_returns_value():
    client.post("/command", json={"command": "SET", "args": ["user:1", "Cuneyt"]})
    response = client.post("/command", json={"command": "GET", "args": ["user:1"]})
    assert response.status_code == 200
    assert response.json() == {"ok": True, "result": "Cuneyt", "error": None}


def test_unknown_command_returns_400():
    response = client.post("/command", json={"command": "FOOBAR", "args": []})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "UNKNOWN_COMMAND"


def test_wrong_argument_count_returns_400():
    response = client.post("/command", json={"command": "SET", "args": ["user:1"]})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_ARGUMENT_COUNT"


def test_wrong_type_returns_409():
    client.post("/command", json={"command": "SET", "args": ["user:1", "Cuneyt"]})
    response = client.post("/command", json={"command": "HSET", "args": ["user:1", "name", "Ayse"]})
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "WRONG_TYPE"


def test_command_name_is_case_insensitive():
    response = client.post("/command", json={"command": "set", "args": ["user:2", "Fatma"]})
    assert response.status_code == 200
    assert response.json()["result"] == "OK"