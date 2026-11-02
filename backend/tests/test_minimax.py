
import pytest

from app.ai.minimax import choose_move
from app.game.board import GameState, ROWS, COLUMNS


def check_winner(board):
    """Temporary test helper until R02's rules are integrated."""

    directions = [
        (0, 1),   # Horizontal
        (1, 0),   # Vertical
        (1, 1),   # Diagonal down-right
        (1, -1),  # Diagonal down-left
    ]

    for row in range(ROWS):
        for col in range(COLUMNS):
            player = board[row][col]

            if player == 0:
                continue

            for dr, dc in directions:
                if all(
                    0 <= row + dr * i < ROWS
                    and 0 <= col + dc * i < COLUMNS
                    and board[row + dr * i][col + dc * i]
                    == player
                    for i in range(4)
                ):
                    return player

    return None


#AI selects column 3 to complete four in a row
def test_minimax_selects_immediate_win():
    game = GameState()

    # Set up three AI pieces in a horizontal row.
    for column in [6, 0, 6, 1, 5, 2, 5]:
        game.apply_move(column)

    assert game.current_player == 2
    assert choose_move(game, 2, check_winner) == 3


#AI blocks the human's winning opportunity
def test_minimax_blocks_immediate_loss():
    game = GameState()

    # Human has three pieces in columns 0, 1, 2.
    for column in [0, 6, 1, 6, 2]:
        game.apply_move(column)

    assert game.current_player == 2
    assert choose_move(game, 2, check_winner) == 3


#AI never selects an unavailable column
def test_minimax_returns_legal_move():
    game = GameState()

    column = choose_move(game, 2, check_winner)

    assert column in game.get_valid_moves()

#Search doesn't change the real game state
def test_minimax_does_not_modify_original():
    game = GameState()
    original = game.clone()

    choose_move(game, 2, check_winner)

    assert game.board == original.board
    assert game.current_player == original.current_player
    assert game.move_count == original.move_count

#Invalid search settings are rejected
def test_minimax_rejects_invalid_depth():
    game = GameState()

    with pytest.raises(ValueError):
        choose_move(game, 0, check_winner)

#AI refuses to play after a completed game
def test_minimax_rejects_finished_game():
    game = GameState()

    # Player 1 achieves a horizontal victory.
    for column in [0, 6, 1, 6, 2, 5, 3]:
        game.apply_move(column)

    with pytest.raises(ValueError):
        choose_move(game, 2, check_winner)
