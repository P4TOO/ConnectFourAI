
from uuid import uuid4

from app.game.board import GameState

# In-memory storage for active games.
games: dict[str, GameState] = {}

#Creates a new board and assigns a unique ID
def create_game() -> tuple[str, GameState]:
    """Create and store a new Connect Four game."""
    game_id = str(uuid4())
    game = GameState()

    games[game_id] = game

    return game_id, game.clone()

#Finds a game using its ID
def get_game(game_id: str) -> GameState | None:
    """Return an independent copy of an existing game."""
    game = games.get(game_id)

    if game is None:
        return None

    return game.clone()

#Saves move in the authoritative Python game state, returns clone of the updated board and the row where the piece landed
def apply_player_move(
    game_id: str, column: int
) -> tuple[GameState, int]:
    """Apply a human move to a stored game."""

    game = games.get(game_id)

    if game is None:
        raise KeyError("Game not found")

    if game.current_player != 1:
        raise ValueError("It is not the human player's turn.")

    # GameState handles gravity, column validation,
    # move counting, and turn switching.
    row = game.apply_move(column)

    return game.clone(), row

