
from fastapi.testclient import TestClient

from app.main import app
from app.api.game_routes import get_winner_checker
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
