
import pytest

import app.services.game_service as game_service

from app.ai.algorithm import AlgorithmId, parse_algorithm
from app.game.board import PLAYER_TWO


# --------------------------------------------------
# Test helpers and fixtures
# --------------------------------------------------

def no_winner(board):
    """Temporary test dependency until April's rules are integrated."""
    return None


@pytest.fixture
def ai_game():
    """Create a game where it is the AI's turn."""
    game_id, _ = game_service.create_game()
    game_service.apply_player_move(game_id, 3)

    yield game_id

    game_service.games.pop(game_id, None)


# --------------------------------------------------
# Algorithm parsing
# --------------------------------------------------

@pytest.mark.parametrize(
    "algorithm, expected",
    [
        ("minimax", AlgorithmId.MINIMAX),
        ("MINIMAX", AlgorithmId.MINIMAX),
        (" mInImAx ", AlgorithmId.MINIMAX),
        ("mcts", AlgorithmId.MCTS),
        (" MCTS ", AlgorithmId.MCTS),
    ],
)
def test_parse_algorithm(algorithm, expected):
    assert parse_algorithm(algorithm) == expected


@pytest.mark.parametrize(
    "algorithm",
    ["unknown", "random", "", "minmax"],
)
def test_parse_algorithm_rejects_invalid(algorithm):
    with pytest.raises(ValueError, match="Invalid algorithm"):
        parse_algorithm(algorithm)


# --------------------------------------------------
# Minimax routing
# --------------------------------------------------

@pytest.mark.parametrize(
    "difficulty, expected_depth",
    [
        ("easy", 2),
        ("medium", 4),
        ("hard", 6),
    ],
)
def test_dispatcher_routes_to_minimax(
    ai_game, difficulty, expected_depth, monkeypatch
):
    received = {}

    def fake_choose_move(game, depth, winner_checker):
        received["game"] = game
        received["depth"] = depth
        received["checker"] = winner_checker
        return 4

    monkeypatch.setattr(
        game_service,
        "choose_move",
        fake_choose_move,
    )

    column = game_service.get_ai_move(
        ai_game,
        "minimax",
        difficulty,
        no_winner,
    )

    assert column == 4
    assert received["depth"] == expected_depth
    assert received["checker"] is no_winner
    assert received["game"].current_player == PLAYER_TWO


# --------------------------------------------------
# MCTS routing (not yet integrated)
# --------------------------------------------------

def test_dispatcher_rejects_unavailable_mcts(ai_game):
    with pytest.raises(
        NotImplementedError,
        match="MCTS is not integrated",
    ):
        game_service.get_ai_move(
            ai_game,
            "mcts",
            "medium",
            no_winner,
        )


# --------------------------------------------------
# Shared validation
# --------------------------------------------------

@pytest.mark.parametrize(
    "algorithm",
    ["minimax", "mcts"],
)
def test_dispatcher_rejects_missing_game(algorithm):
    with pytest.raises(KeyError):
        game_service.get_ai_move(
            "nonexistent-game",
            algorithm,
            "easy",
            no_winner,
        )


@pytest.mark.parametrize(
    "algorithm",
    ["minimax", "mcts"],
)
def test_dispatcher_rejects_human_turn(algorithm):
    game_id, _ = game_service.create_game()

    try:
        with pytest.raises(
            ValueError,
            match="AI player's turn",
        ):
            game_service.get_ai_move(
                game_id,
                algorithm,
                "easy",
                no_winner,
            )
    finally:
        game_service.games.pop(game_id, None)


# --------------------------------------------------
# Board integrity
# --------------------------------------------------

def test_dispatcher_does_not_modify_game(ai_game):
    before = game_service.get_game(ai_game)

    column = game_service.get_ai_move(
        ai_game,
        "minimax",
        "easy",
        no_winner,
    )

    after = game_service.get_game(ai_game)

    assert column in before.get_valid_moves()
    assert after.board == before.board
    assert after.current_player == before.current_player
    assert after.move_count == before.move_count
    

# --------------------------------------------------
# MCTS integration contract
# --------------------------------------------------

def test_dispatcher_accepts_injected_mcts(ai_game):
    """An injected MCTS selector can return a legal column."""
    calls = []

    def fake_mcts(game, difficulty):
        calls.append((game, difficulty))
        return 4

    column = game_service.get_ai_move(
        ai_game,
        "mcts",
        "medium",
        no_winner,
        mcts_selector=fake_mcts,
    )

    assert column == 4
    assert len(calls) == 1
    assert calls[0][1] == "medium"
    assert calls[0][0].current_player == PLAYER_TWO


@pytest.mark.parametrize(
    "invalid_column",
    [-1, 7, 100],
)
def test_dispatcher_rejects_invalid_mcts_column(
    ai_game, invalid_column
):
    def fake_mcts(game, difficulty):
        return invalid_column

    with pytest.raises(ValueError, match="Invalid Column"):
        game_service.get_ai_move(
            ai_game,
            "mcts",
            "medium",
            no_winner,
            mcts_selector=fake_mcts,
        )


@pytest.mark.parametrize(
    "invalid_column",
    [3.5, "3", True, None],
)
def test_dispatcher_rejects_invalid_mcts_type(
    ai_game, invalid_column
):
    def fake_mcts(game, difficulty):
        return invalid_column

    with pytest.raises(ValueError, match="Invalid data type"):
        game_service.get_ai_move(
            ai_game,
            "mcts",
            "medium",
            no_winner,
            mcts_selector=fake_mcts,
        )


def test_dispatcher_rejects_finished_game(ai_game):
    """A completed game must be rejected before either AI runs."""
    calls = []

    def finished_game(board):
        return 1

    def fake_mcts(game, difficulty):
        calls.append("called")
        return 3

    for algorithm in ["minimax", "mcts"]:
        with pytest.raises(ValueError, match="Game is already over"):
            game_service.get_ai_move(
                ai_game,
                algorithm,
                "easy",
                finished_game,
                mcts_selector=fake_mcts,
            )

    # Winner detection should prevent MCTS from being called.
    assert calls == []


def test_dispatcher_mcts_preserves_original_game(ai_game):
    """Selecting an MCTS move must not change stored game state."""
    before = game_service.get_game(ai_game)

    def fake_mcts(game, difficulty):
        # Simulate an algorithm manipulating its search state.
        game.apply_move(4)
        return 4

    column = game_service.get_ai_move(
        ai_game,
        "mcts",
        "medium",
        no_winner,
        mcts_selector=fake_mcts,
    )

    after = game_service.get_game(ai_game)

    assert column == 4
    assert after.board == before.board
    assert after.current_player == before.current_player
    assert after.move_count == before.move_count

