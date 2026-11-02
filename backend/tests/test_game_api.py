
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_game():
    response = client.post("/api/games")

    assert response.status_code == 201

    data = response.json()

    assert "game_id" in data
    assert len(data["board"]) == 6
    assert all(len(row) == 7 for row in data["board"])
    assert all(cell == 0 for row in data["board"] for cell in row)
    assert data["current_player"] == 1
    assert data["status"] == "ongoing"


def test_get_existing_game():
    created = client.post("/api/games").json()
    game_id = created["game_id"]

    response = client.get(f"/api/games/{game_id}")

    assert response.status_code == 200
    assert response.json()["board"] == created["board"]


def test_get_nonexistent_game():
    response = client.get("/api/games/invalid-id")

    assert response.status_code == 404


def test_unique_game_ids():
    game1 = client.post("/api/games").json()
    game2 = client.post("/api/games").json()

    assert game1["game_id"] != game2["game_id"]


def test_apply_player_move():
    created = client.post("/api/games").json()
    game_id = created["game_id"]

    response = client.post(
        f"/api/games/{game_id}/moves",
        json={"column": 3},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["board"][5][3] == 1
    assert data["current_player"] == 2
    assert data["last_move"] == {
        "row": 5,
        "column": 3,
        "player": 1,
    }


def test_move_updates_stored_game():
    created = client.post("/api/games").json()
    game_id = created["game_id"]

    client.post(
        f"/api/games/{game_id}/moves",
        json={"column": 4},
    )

    response = client.get(f"/api/games/{game_id}")

    assert response.status_code == 200
    assert response.json()["board"][5][4] == 1


def test_reject_consecutive_human_moves():
    created = client.post("/api/games").json()
    game_id = created["game_id"]

    first = client.post(
        f"/api/games/{game_id}/moves",
        json={"column": 3},
    )

    second = client.post(
        f"/api/games/{game_id}/moves",
        json={"column": 4},
    )

    assert first.status_code == 200
    assert second.status_code == 400


def test_reject_invalid_column():
    created = client.post("/api/games").json()
    game_id = created["game_id"]

    response = client.post(
        f"/api/games/{game_id}/moves",
        json={"column": 7},
    )

    assert response.status_code == 422


def test_move_nonexistent_game():
    response = client.post(
        "/api/games/invalid-id/moves",
        json={"column": 3},
    )

    assert response.status_code == 404
