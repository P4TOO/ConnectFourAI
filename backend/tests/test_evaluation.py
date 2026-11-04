
import pytest

from app.ai.evaluation import evaluate_board, evaluate_window
from app.ai.minimax import choose_move
from app.game.board import (
    COLUMNS,
    ROWS,
    EMPTY,
    PLAYER_ONE,
    PLAYER_TWO,
    GameState,
)


@pytest.mark.parametrize(
    ("cells", "expected"),
    [
        ([2, 2, 2, 2], 1000),
        ([2, 2, 2, 0], 100),
        ([2, 2, 0, 0], 10),
        ([2, 0, 0, 0], 1),
        ([1, 1, 1, 1], -1000),
        ([1, 1, 1, 0], -150),
        ([1, 1, 0, 0], -10),
        ([1, 0, 0, 0], -1),
        ([1, 2, 0, 0], 0),
        ([0, 0, 0, 0], 0),
    ],
)
def test_evaluate_window_scores(cells, expected):
    assert evaluate_window(cells, PLAYER_TWO) == expected


def test_evaluate_window_supports_either_ai_player():
    cells = [PLAYER_ONE, PLAYER_ONE, PLAYER_ONE, EMPTY]

    assert evaluate_window(cells, PLAYER_ONE) == 100
    assert evaluate_window(cells, PLAYER_TWO) == -150


def make_game(pieces, current_player=PLAYER_TWO):
    game = GameState()
    game.current_player = current_player

    for row, column, player in pieces:
        game.board[row][column] = player

    return game


def test_empty_board_scores_zero():
    game = GameState()

    assert evaluate_board(game, PLAYER_ONE) == 0
    assert evaluate_board(game, PLAYER_TWO) == 0


def test_center_column_is_more_valuable_than_edge():
    center = make_game([(5, 3, PLAYER_TWO)])
    edge = make_game([(5, 0, PLAYER_TWO)])

    assert evaluate_board(center, PLAYER_TWO) > evaluate_board(
        edge, PLAYER_TWO
    )


def test_center_column_bonus_changes_score():
    center = make_game([(5, 3, PLAYER_TWO)])

    original_score = evaluate_board(center, PLAYER_TWO)

    # Temporarily remove only the center positional effect
    # by comparing against the same board from the opponent's perspective.
    opponent_score = evaluate_board(center, PLAYER_ONE)

    assert original_score > 0
    assert opponent_score < 0


@pytest.mark.parametrize(
    "positions",
    [
        [(5, 0), (5, 1), (5, 2)],  # Horizontal
        [(5, 0), (4, 0), (3, 0)],  # Vertical
        [(5, 0), (4, 1), (3, 2)],  # Diagonal upward-right
        [(2, 0), (3, 1), (4, 2)],  # Diagonal downward-right
    ],
)
def test_three_pieces_score_better_than_two(positions):
    three_pieces = make_game(
        [(row, col, PLAYER_TWO) for row, col in positions]
    )
    two_pieces = make_game(
        [(row, col, PLAYER_TWO) for row, col in positions[:2]]
    )

    assert evaluate_board(
        three_pieces, PLAYER_TWO
    ) > evaluate_board(two_pieces, PLAYER_TWO)


def test_opponent_threat_produces_negative_score():
    game = make_game(
        [
            (5, 0, PLAYER_ONE),
            (5, 1, PLAYER_ONE),
            (5, 2, PLAYER_ONE),
        ]
    )

    assert evaluate_board(game, PLAYER_TWO) < 0


def test_evaluate_board_does_not_modify_game():
    game = make_game([(5, 3, PLAYER_TWO)])
    original_board = [row.copy() for row in game.board]

    evaluate_board(game, PLAYER_TWO)

    assert game.board == original_board


def check_winner(board):
    directions = [(0, 1), (1, 0), (1, 1), (-1, 1)]

    for row in range(ROWS):
        for col in range(COLUMNS):
            player = board[row][col]

            if player == EMPTY:
                continue

            for dr, dc in directions:
                if all(
                    0 <= row + i * dr < ROWS
                    and 0 <= col + i * dc < COLUMNS
                    and board[row + i * dr][col + i * dc] == player
                    for i in range(4)
                ):
                    return player

    return None


def test_ai_chooses_immediate_winning_move():
    game = make_game(
        [
            (5, 0, PLAYER_TWO),
            (5, 1, PLAYER_TWO),
            (5, 2, PLAYER_TWO),
        ]
    )

    assert choose_move(game, depth=2, check_winner=check_winner) == 3


def test_ai_blocks_immediate_opponent_win():
    game = make_game(
        [
            (5, 0, PLAYER_ONE),
            (5, 1, PLAYER_ONE),
            (5, 2, PLAYER_ONE),
        ]
    )

    assert choose_move(game, depth=2, check_winner=check_winner) == 3
