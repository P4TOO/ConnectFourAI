
from fastapi.testclient import TestClient

from app.main import app
from app.api.schemas import GameCreateRequest, MoveRequest

client = TestClient(app)


def test_ping_endpoint():
    response = client.get("/api/ping")

    assert response.status_code == 200
    assert response.json() == {
        "message": "ConnectFourAI API connected"
    }


def test_move_request_schema():
    request = MoveRequest(column=3)

    assert request.column == 3


def test_game_create_schema_defaults():
    request = GameCreateRequest()

    assert request.algorithm == "minimax"
    assert request.difficulty == "medium"
