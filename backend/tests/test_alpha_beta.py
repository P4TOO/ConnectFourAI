
import pytest

import app.ai.minimax as minimax_module
from app.ai.minimax import choose_move, minimax
from app.game.board import (
    GameState,
    PLAYER_ONE,
    PLAYER_TWO,
    EMPTY,
    ROWS,
    COLUMNS,
)


# --------------------------------------------------
# Test helpers
# --------------------------------------------------

def check_winner(board):
    directions = [(0, 1), (1, 0), (1, 1), (-1, 1)]

    for row in range(ROWS):
        for column in range(COLUMNS):
            player = board[row][column]

            if player == EMPTY:
                continue

            for dr, dc in directions:
                if all(
                    0 <= row + i * dr < ROWS
                    and 0 <= column + i * dc < COLUMNS
                    and board[row + i * dr][column + i * dc] == player
                    for i in range(4)
                ):
                    return player

    return None


def make_game(pieces, current_player=PLAYER_TWO):
    game = GameState()
    game.current_player = current_player

    for row, column, player in pieces:
        game.board[row][column] = player

    return game


# Reference implementation without alpha-beta pruning.
# Used only to verify that pruning preserves Minimax's result.
def reference_minimax(game, depth, ai_player, winner_check):
    winner = winner_check(game.board)

    if winner is not None:
        if winner == ai_player:
            return 1_000_000 + depth
        return -1_000_000 - depth

    available_columns = game.get_valid_moves()

    if not available_columns:
        return 0

    if depth == 0:
        return minimax_module.evaluate_board(game, ai_player)

    maximizing = game.current_player == ai_player
    scores = []

    for column in available_columns:
        clone = game.clone()
        clone.apply_move(column)

        score = reference_minimax(
            clone, depth - 1, ai_player, winner_check
        )
        scores.append(score)

    return max(scores) if maximizing else min(scores)


def reference_choose_move(game, depth, winner_check):
    ai_player = game.current_player
    best_score = float("-inf")
    best_column = None

    for column in game.get_valid_moves():
        clone = game.clone()
        clone.apply_move(column)

        score = reference_minimax(
            clone, depth - 1, ai_player, winner_check
        )

        if score > best_score:
            best_score = score
            best_column = column

    return best_column


# --------------------------------------------------
# Correctness tests
# --------------------------------------------------

def test_alpha_beta_chooses_immediate_win():
    game = make_game([
        (5, 0, PLAYER_TWO),
        (5, 1, PLAYER_TWO),
        (5, 2, PLAYER_TWO),
    ])

    assert choose_move(game, 3, check_winner) == 3


def test_alpha_beta_blocks_immediate_loss():
    game = make_game([
        (5, 0, PLAYER_ONE),
        (5, 1, PLAYER_ONE),
        (5, 2, PLAYER_ONE),
    ])

    assert choose_move(game, 3, check_winner) == 3


@pytest.mark.parametrize(
    "moves",
    [
        [],
        [3, 2, 3, 2],
        [0, 1, 0, 1, 2, 3],
    ],
)
def test_alpha_beta_matches_reference_minimax(moves):
    game = GameState()

    for column in moves:
        game.apply_move(column)

    ai_player = game.current_player
    depth = 3

    expected = reference_minimax(
        game, depth, ai_player, check_winner
    )

    actual = minimax(
        game,
        depth,
        ai_player,
        check_winner,
        float("-inf"),
        float("inf"),
    )

    assert actual == expected


@pytest.mark.parametrize(
    "moves",
    [
        [],
        [3, 2, 3, 2],
        [0, 1, 0, 1, 2, 3],
    ],
)
def test_alpha_beta_selects_same_move_as_reference(moves):
    game = GameState()

    for column in moves:
        game.apply_move(column)

    expected = reference_choose_move(
        game, 3, check_winner
    )

    actual = choose_move(game, 3, check_winner)

    assert actual == expected


def test_terminal_scores_prioritize_wins_and_losses():
    winning_game = make_game([
        (5, 0, PLAYER_TWO),
        (5, 1, PLAYER_TWO),
        (5, 2, PLAYER_TWO),
        (5, 3, PLAYER_TWO),
    ])

    win_score = minimax(
        winning_game, 2, PLAYER_TWO,
        check_winner, float("-inf"), float("inf")
    )

    loss_score = minimax(
        winning_game, 2, PLAYER_ONE,
        check_winner, float("-inf"), float("inf")
    )

    assert win_score == 1_000_002
    assert loss_score == -1_000_002


def test_alpha_beta_does_not_modify_original_state():
    game = GameState()
    game.apply_move(3)
    game.apply_move(2)

    original_board = [row.copy() for row in game.board]
    original_player = game.current_player
    original_moves = game.move_count

    choose_move(game, 3, check_winner)

    assert game.board == original_board
    assert game.current_player == original_player
    assert game.move_count == original_moves


def test_alpha_beta_returns_legal_move():
    game = GameState()

    for column in [3, 2, 3, 2]:
        game.apply_move(column)

    chosen_column = choose_move(game, 3, check_winner)

    assert chosen_column in game.get_valid_moves()


# --------------------------------------------------
# Pruning efficiency test
# --------------------------------------------------

def test_alpha_beta_prunes_unnecessary_branches(monkeypatch):
    game = GameState()
    ai_player = game.current_player
    depth = 4

    evaluation_calls = {"count": 0}

    # Give every nonterminal leaf the same score.
    # This creates a predictable opportunity to prune.
    def flat_evaluation(game_state, player):
        evaluation_calls["count"] += 1
        return 0

    monkeypatch.setattr(
        minimax_module,
        "evaluate_board",
        flat_evaluation,
    )

    def no_winner(board):
        return None

    # Ordinary Minimax explores every possible branch.
    reference_score = reference_minimax(
        game, depth, ai_player, no_winner
    )
    reference_count = evaluation_calls["count"]

    # Reset counter before alpha-beta search.
    evaluation_calls["count"] = 0

    alpha_beta_score = minimax(
        game,
        depth,
        ai_player,
        no_winner,
        float("-inf"),
        float("inf"),
    )

    alpha_beta_count = evaluation_calls["count"]

    assert alpha_beta_score == reference_score
    assert alpha_beta_count < reference_count
    assert alpha_beta_count > 0

    print(f"\nRegular Minimax evaluations: {reference_count}")
    print(f"Alpha-Beta evaluations: {alpha_beta_count}")
    print(
        "Reduction: "
        f"{(1 - alpha_beta_count / reference_count) * 100:.2f}%"
    )
