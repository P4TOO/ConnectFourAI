
from collections.abc import Callable

from app.game.board import GameState, PLAYER_ONE, PLAYER_TWO

# Returns the winning player, or None when nobody has won.
WinnerCheck = Callable[[list[list[int]]], int | None]

WIN_SCORE = 1000


def minimax(
    game: GameState,
    depth: int,
    ai_player: int,
    check_winner: WinnerCheck,
) -> int:
    """Evaluate a game state using depth-limited Minimax."""

    winner = check_winner(game.board)

    # Terminal states: AI victory or human victory.
    if winner is not None:
        if winner == ai_player:
            return WIN_SCORE + depth
        return -WIN_SCORE - depth

    valid_moves = game.get_valid_moves()

    # Draw or depth limit reached.
    if not valid_moves or depth == 0:
        return 0

    maximizing = game.current_player == ai_player

    if maximizing:
        best_score = float("-inf")

        for column in valid_moves:
            simulated = game.clone()
            simulated.apply_move(column)

            score = minimax(
                simulated, depth - 1, ai_player, check_winner
            )

            best_score = max(best_score, score)

        return best_score

    else:
        best_score = float("inf")

        for column in valid_moves:
            simulated = game.clone()
            simulated.apply_move(column)

            score = minimax(
                simulated, depth - 1, ai_player, check_winner
            )

            best_score = min(best_score, score)

        return best_score


def choose_move(
    game: GameState,
    depth: int,
    check_winner: WinnerCheck,
) -> int:
    """Choose the best available move for the current AI player."""

    if depth < 1:
        raise ValueError("Search depth must be at least 1.")

    ai_player = game.current_player

    if ai_player not in (PLAYER_ONE, PLAYER_TWO):
        raise ValueError("Invalid current player.")

    if check_winner(game.board) is not None:
        raise ValueError("The game has already been won.")

    valid_moves = game.get_valid_moves()

    if not valid_moves:
        raise ValueError("No legal moves available.")

    best_score = float("-inf")
    best_column = valid_moves[0]

    for column in valid_moves:
        simulated = game.clone()
        simulated.apply_move(column)

        score = minimax(
            simulated, depth - 1, ai_player, check_winner
        )

        if score > best_score:
            best_score = score
            best_column = column

    return best_column
