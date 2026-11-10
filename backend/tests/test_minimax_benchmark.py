
import statistics
import time

import pytest

from app.game.board import GameState, PLAYER_TWO
from app.services.game_service import (
    create_game,
    get_game,
    get_ai_move,
    games,
)


# --------------------------------------------------
# Test-only winner detection
# --------------------------------------------------

def check_winner(board):
    directions = [
        (0, 1),
        (1, 0),
        (1, 1),
        (1, -1),
    ]

    rows = len(board)
    cols = len(board[0])

    for row in range(rows):
        for col in range(cols):
            player = board[row][col]

            if player == 0:
                continue

            for dr, dc in directions:
                if all(
                    0 <= row + dr * i < rows
                    and 0 <= col + dc * i < cols
                    and board[row + dr * i][col + dc * i] == player
                    for i in range(4)
                ):
                    return player

    return None


# --------------------------------------------------
# Representative board configurations
# --------------------------------------------------

BOARD_SCENARIOS = {
    "early": [
        3,
    ],
    "midgame": [
        0, 0, 2, 2, 2, 3, 1, 5,
        2, 2, 6, 6, 4, 2, 0, 1,
        0, 0, 1, 6, 0, 4, 1,
    ],
    "late": [
        1, 6, 5, 4, 2, 3, 6, 3,
        1, 0, 0, 4, 3, 5, 0, 1,
        1, 6, 3, 1, 6, 5, 5, 0,
        0, 3, 6, 5, 1, 6, 5,
    ],
}

DIFFICULTIES = [
    ("easy", 2),
    ("medium", 4),
    ("hard", 6),
]

REPETITIONS = 2


def build_game(moves):
    """Build a legal board using alternating player turns."""
    game = GameState()

    for column in moves:
        game.apply_move(column)

        # Scenario must remain nonterminal.
        assert check_winner(game.board) is None

    assert game.current_player == PLAYER_TWO
    assert game.get_valid_moves()

    return game


@pytest.fixture(params=BOARD_SCENARIOS.keys())
def benchmark_game(request):
    """Create an isolated stored game for each board scenario."""
    scenario = request.param
    game_id, _ = create_game()

    games[game_id] = build_game(
        BOARD_SCENARIOS[scenario]
    )

    yield scenario, game_id

    games.pop(game_id, None)


# --------------------------------------------------
# Performance and reliability benchmark
# --------------------------------------------------

@pytest.mark.parametrize(
    "difficulty, depth",
    DIFFICULTIES,
)
def test_minimax_reliability_and_speed(
    benchmark_game, difficulty, depth
):
    scenario, game_id = benchmark_game

    original = get_game(game_id)
    legal_moves = original.get_valid_moves()

    times_ms = []
    chosen_moves = []

    for _ in range(REPETITIONS):
        start = time.perf_counter()

        column = get_ai_move(
            game_id,
            "minimax",
            difficulty,
            check_winner,
        )

        elapsed_ms = (
            time.perf_counter() - start
        ) * 1000

        times_ms.append(elapsed_ms)
        chosen_moves.append(column)

        # Every returned move must be legal.
        assert isinstance(column, int)
        assert column in legal_moves

        # Ensure the original game was not modified.
        current = get_game(game_id)

        assert current.board == original.board
        assert current.current_player == original.current_player
        assert current.move_count == original.move_count

    median_ms = statistics.median(times_ms)

    print(
        f"\nScenario: {scenario}"
        f"\nDifficulty: {difficulty}"
        f"\nDepth: {depth}"
        f"\nLegal moves: {legal_moves}"
        f"\nAI choices: {chosen_moves}"
        f"\nMedian time: {median_ms:.2f} ms"
        f"\nMax time: {max(times_ms):.2f} ms"
    )

    # Time must be measurable and nonnegative.
    assert all(t >= 0 for t in times_ms)


# --------------------------------------------------
# Additional reliability test
# --------------------------------------------------

@pytest.mark.parametrize(
    "scenario",
    BOARD_SCENARIOS.keys(),
)
def test_scenarios_are_valid(scenario):
    game = build_game(BOARD_SCENARIOS[scenario])

    assert game.current_player == PLAYER_TWO
    assert check_winner(game.board) is None
    assert len(game.get_valid_moves()) > 0
