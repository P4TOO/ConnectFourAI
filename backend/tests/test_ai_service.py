
import pytest

import app.services.game_service as game_service
from app.game.board import (
    COLUMNS,
    ROWS,
    EMPTY,
    PLAYER_ONE,
    PLAYER_TWO,
)


# --------------------------------------------------
# Test helpers
# --------------------------------------------------

def check_winner(board):
    """Temporary winner checker until April's implementation is ready."""
    directions = [
        (0, 1),   # Horizontal
        (1, 0),   # Vertical
        (1, 1),   # Diagonal down-right
        (1, -1),  # Diagonal down-left
    ]

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


@pytest.fixture
def ai_game():
    """Create a game where it is the AI's turn."""
    game_id, _ = game_service.create_game()
    game_service.apply_player_move(game_id, 3)

    yield game_id

    game_service.games.pop(game_id, None)


# --------------------------------------------------
# Difficulty selection
# --------------------------------------------------

@pytest.mark.parametrize(
    "difficulty, expected_depth",
    [
        ("easy", 2),
        ("medium", 4),
        ("hard", 6),
        (" EASY ", 2),
        ("MeDiUm", 4),
    ],
)
def test_difficulty_maps_to_correct_depth(
    ai_game, difficulty, expected_depth, monkeypatch
):
    received = {}

    def fake_choose_move(game, depth, winner_checker):
        received["depth"] = depth
        received["checker"] = winner_checker
        return 3

    monkeypatch.setattr(
        game_service,
        "choose_move",
        fake_choose_move,
    )

    move = game_service.get_ai_move(
        ai_game, difficulty, check_winner
    )

    assert move == 3
    assert received["depth"] == expected_depth
    assert received["checker"] is check_winner


# --------------------------------------------------
# Legal move selection
# --------------------------------------------------

def test_ai_returns_legal_move(ai_game):
    game = game_service.get_game(ai_game)

    move = game_service.get_ai_move(
        ai_game, "easy", check_winner
    )

    assert isinstance(move, int)
    assert move in game.get_valid_moves()
    assert 0 <= move < COLUMNS


def test_ai_avoids_full_column(ai_game):
    stored_game = game_service.games[ai_game]

    # Fill column 0 without creating a four-in-a-row.
    for row in range(ROWS):
        stored_game.board[row][0] = (
            PLAYER_ONE if row % 2 == 0 else PLAYER_TWO
        )

    original_valid_moves = stored_game.get_valid_moves()

    assert 0 not in original_valid_moves

    move = game_service.get_ai_move(
        ai_game, "easy", check_winner
    )

    assert move in original_valid_moves
    assert move != 0


# --------------------------------------------------
# Error handling
# --------------------------------------------------

def test_ai_rejects_missing_game():
    with pytest.raises(KeyError):
        game_service.get_ai_move(
            "invalid-game-id",
            "easy",
            check_winner,
        )


def test_ai_rejects_human_turn():
    game_id, _ = game_service.create_game()

    try:
        with pytest.raises(ValueError, match="AI player's turn"):
            game_service.get_ai_move(
                game_id,
                "easy",
                check_winner,
            )
    finally:
        game_service.games.pop(game_id, None)


@pytest.mark.parametrize(
    "difficulty",
    ["expert", "impossible", "", "123"],
)
def test_ai_rejects_invalid_difficulty(ai_game, difficulty):
    with pytest.raises(ValueError, match="Invalid difficulty"):
        game_service.get_ai_move(
            ai_game,
            difficulty,
            check_winner,
        )


# --------------------------------------------------
# State integrity
# --------------------------------------------------

def test_ai_does_not_modify_stored_game(ai_game):
    before = game_service.get_game(ai_game)

    move = game_service.get_ai_move(
        ai_game, "easy", check_winner
    )

    after = game_service.get_game(ai_game)

    assert move in before.get_valid_moves()
    assert after.board == before.board
    assert after.current_player == before.current_player
    assert after.move_count == before.move_count


def test_ai_does_not_apply_selected_move(ai_game):
    before = game_service.get_game(ai_game)

    # Repeated requests should not place any pieces.
    game_service.get_ai_move(
        ai_game, "easy", check_winner
    )
    game_service.get_ai_move(
        ai_game, "easy", check_winner
    )

    after = game_service.get_game(ai_game)

    assert after.move_count == before.move_count
    assert after.current_player == PLAYER_TWO
    assert after.board == before.board
