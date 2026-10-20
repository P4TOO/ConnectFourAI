
import pytest

from app.game.board import (
    COLUMNS,
    ROWS,
    GameState,
    PLAYER_ONE,
    PLAYER_TWO,
)

#Verifies that a new game creates a 6x7 board containing only zeros, starts with Player 1, and has a move count of zero
def test_initial_board():
    game = GameState()

    assert len(game.board) == ROWS
    assert all(len(row) == COLUMNS for row in game.board)
    assert all(cell == 0 for row in game.board for cell in row)
    assert game.current_player == PLAYER_ONE
    assert game.move_count == 0


#Places a piece in column 3 and verifies that it lands in row 5, the bottom row. Also checks that the move count increases
def test_piece_drops_to_bottom():
    game = GameState()

    row = game.apply_move(3)

    assert row == 5
    assert game.board[5][3] == PLAYER_ONE
    assert game.move_count == 1

#Makes two consecutive moves and verifies that the current player changes from Player 1 to Player 2, then back to Player 1.
def test_turn_alternates():
    game = GameState()

    game.apply_move(3)
    assert game.current_player == PLAYER_TWO

    game.apply_move(4)
    assert game.current_player == PLAYER_ONE
    assert game.move_count == 2


#Places two pieces in the same column and checks that the second piece lands directly above the first
def test_pieces_stack_in_column():
    game = GameState()

    assert game.apply_move(2) == 5
    assert game.apply_move(2) == 4

    assert game.board[5][2] == PLAYER_ONE
    assert game.board[4][2] == PLAYER_TWO

#Fills an entire column with six pieces, then attempts another move in that column
def test_full_column_is_rejected():
    game = GameState()

    for _ in range(ROWS):
        game.apply_move(0)

    assert 0 not in game.get_valid_moves()

    with pytest.raises(ValueError):
        game.apply_move(0)

    assert game.move_count == ROWS

#Attempts moves using invalid inputs: -1, 7, 1.5, "3", and True
@pytest.mark.parametrize("column", [-1, 7, 1.5, "3", True])
def test_invalid_columns(column):
    game = GameState()

    with pytest.raises(ValueError):
        game.apply_move(column)

    assert game.move_count == 0
    assert game.current_player == PLAYER_ONE

#Creates a copy of an existing game, applies a move to the copy, and verifies that the original remaisn unchanged
def test_clone_is_independent():
    original = GameState()
    original.apply_move(3)

    cloned = original.clone()
    cloned.apply_move(4)

    assert original.board[5][4] == 0
    assert cloned.board[5][4] == PLAYER_TWO

    assert original.move_count == 1
    assert cloned.move_count == 2
    assert original.current_player == PLAYER_TWO
    assert cloned.current_player == PLAYER_ONE

#Checks that all seven columns are available when a game begins
def test_valid_moves_on_empty_board():
    game = GameState()

    assert game.get_valid_moves() == list(range(COLUMNS))
