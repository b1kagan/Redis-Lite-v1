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

def test_del_command_via_api():
    client.post("/command", json={"command": "SET", "args": ["k1", "v1"]})
    response = client.post("/command", json={"command": "DEL", "args": ["k1"]})
    assert response.json()["result"] == 1


def test_incr_command_via_api():
    response = client.post("/command", json={"command": "INCR", "args": ["counter"]})
    assert response.json()["result"] == 1


def test_hget_command_via_api():
    client.post("/command", json={"command": "HSET", "args": ["u1", "name", "Ayse"]})
    response = client.post("/command", json={"command": "HGET", "args": ["u1", "name"]})
    assert response.json()["result"] == "Ayse"


def test_hdel_command_via_api():
    client.post("/command", json={"command": "HSET", "args": ["u2", "name", "Ayse"]})
    response = client.post("/command", json={"command": "HDEL", "args": ["u2", "name"]})
    assert response.json()["result"] == 1


def test_hgetall_command_via_api():
    client.post("/command", json={"command": "HSET", "args": ["u3", "name", "Ayse"]})
    response = client.post("/command", json={"command": "HGETALL", "args": ["u3"]})
    assert response.json()["result"] == {"name": "Ayse"}


def test_zadd_command_via_api():
    response = client.post("/command", json={"command": "ZADD", "args": ["lb", "150", "p1"]})
    assert response.json()["result"] == 1


def test_zrange_command_via_api():
    client.post("/command", json={"command": "ZADD", "args": ["lb2", "150", "p1"]})
    response = client.post("/command", json={"command": "ZRANGE", "args": ["lb2", "0", "-1"]})
    assert response.json()["result"] == ["p1"]


def test_zrem_command_via_api():
    client.post("/command", json={"command": "ZADD", "args": ["lb3", "150", "p1"]})
    response = client.post("/command", json={"command": "ZREM", "args": ["lb3", "p1"]})
    assert response.json()["result"] == 1


def test_zscore_command_via_api():
    client.post("/command", json={"command": "ZADD", "args": ["lb4", "150", "p1"]})
    response = client.post("/command", json={"command": "ZSCORE", "args": ["lb4", "p1"]})
    assert response.json()["result"] == 150