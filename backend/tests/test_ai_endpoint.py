
from fastapi.testclient import TestClient

from app.main import app
from app.api.game_routes import (
    get_winner_checker,
    get_mcts_selector,
)
from app.game.board import ROWS, COLUMNS, EMPTY


def check_winner(board):
    """Test-only winner checker."""
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

    for row in range(ROWS):
        for col in range(COLUMNS):
            player = board[row][col]

            if player == EMPTY:
                continue

            for dr, dc in directions:
                if all(
                    0 <= row + dr * i < ROWS
                    and 0 <= col + dc * i < COLUMNS
                    and board[row + dr * i][col + dc * i] == player
                    for i in range(4)
                ):
                    return player

    return None


def test_ai_move_endpoint():
    app.dependency_overrides[get_winner_checker] = (
        lambda: check_winner
    )

    try:
        with TestClient(app) as client:
            created = client.post("/api/games").json()
            game_id = created["game_id"]

            # Human makes the first move.
            human_response = client.post(
                f"/api/games/{game_id}/moves",
                json={"column": 3},
            )
            assert human_response.status_code == 200

            before = client.get(
                f"/api/games/{game_id}"
            ).json()

            response = client.post(
                f"/api/games/{game_id}/ai-move",
                json={"difficulty": "easy"},
            )

            assert response.status_code == 200

            column = response.json()["column"]

            assert isinstance(column, int)
            assert 0 <= column <= 6
            assert before["board"][0][column] == EMPTY

            # Selecting a move must not modify the board.
            after = client.get(
                f"/api/games/{game_id}"
            ).json()

            assert after["board"] == before["board"]
            assert after["current_player"] == 2

    finally:
        app.dependency_overrides.pop(
            get_winner_checker, None
        )


# --------------------------------------------------
# W6-R01-T1: Unified AI endpoint integration
# --------------------------------------------------

def test_mcts_endpoint_with_injected_selector():
    """MCTS requests reach the injected implementation."""

    calls = []

    def fake_mcts(game, difficulty):
        calls.append({
            "difficulty": difficulty,
            "player": game.current_player,
        })
        return 4

    app.dependency_overrides[get_winner_checker] = (
        lambda: check_winner
    )
    app.dependency_overrides[get_mcts_selector] = (
        lambda: fake_mcts
    )

    try:
        with TestClient(app) as client:
            created = client.post("/api/games").json()
            game_id = created["game_id"]

            # Human moves first.
            human_response = client.post(
                f"/api/games/{game_id}/moves",
                json={"column": 3},
            )

            assert human_response.status_code == 200

            before = client.get(
                f"/api/games/{game_id}"
            ).json()

            response = client.post(
                f"/api/games/{game_id}/ai-move",
                json={
                    "algorithm": "mcts",
                    "difficulty": "medium",
                },
            )

            assert response.status_code == 200
            assert response.json() == {"column": 4}

            # Verify MCTS received the correct parameters.
            assert len(calls) == 1
            assert calls[0]["difficulty"] == "medium"
            assert calls[0]["player"] == 2

            # Selecting a move must not change the board.
            after = client.get(
                f"/api/games/{game_id}"
            ).json()

            assert after["board"] == before["board"]
            assert after["current_player"] == 2

    finally:
        app.dependency_overrides.pop(
            get_winner_checker, None
        )
        app.dependency_overrides.pop(
            get_mcts_selector, None
        )


def test_mcts_endpoint_without_implementation():
    """Unavailable MCTS returns a clear HTTP 503."""

    app.dependency_overrides[get_winner_checker] = (
        lambda: check_winner
    )

    try:
        with TestClient(app) as client:
            created = client.post("/api/games").json()
            game_id = created["game_id"]

            client.post(
                f"/api/games/{game_id}/moves",
                json={"column": 3},
            )

            response = client.post(
                f"/api/games/{game_id}/ai-move",
                json={
                    "algorithm": "mcts",
                    "difficulty": "medium",
                },
            )

            assert response.status_code == 503
            assert "MCTS is not integrated" in (
                response.json()["detail"]
            )

    finally:
        app.dependency_overrides.pop(
            get_winner_checker, None
        )


def test_mcts_endpoint_rejects_illegal_move():
    """The API rejects an invalid column from MCTS."""

    def fake_mcts(game, difficulty):
        return 7

    app.dependency_overrides[get_winner_checker] = (
        lambda: check_winner
    )
    app.dependency_overrides[get_mcts_selector] = (
        lambda: fake_mcts
    )

    try:
        with TestClient(app) as client:
            created = client.post("/api/games").json()
            game_id = created["game_id"]

            client.post(
                f"/api/games/{game_id}/moves",
                json={"column": 3},
            )

            response = client.post(
                f"/api/games/{game_id}/ai-move",
                json={
                    "algorithm": "mcts",
                    "difficulty": "easy",
                },
            )

            assert response.status_code == 400
            assert "Invalid Column" in (
                response.json()["detail"]
            )

    finally:
        app.dependency_overrides.pop(
            get_winner_checker, None
        )
        app.dependency_overrides.pop(
            get_mcts_selector, None
        )
