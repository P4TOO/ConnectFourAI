
from collections.abc import Callable
from uuid import uuid4

from app.ai.difficulty import parse_difficulty
from app.ai.algorithm import AlgorithmId, parse_algorithm
from app.ai.minimax import choose_move
from app.game.board import GameState, PLAYER_ONE, PLAYER_TWO

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

def get_ai_move(game_id: str, algorithm: str, difficulty: str, check_winner: Callable, mcts_selector: Callable | None = None) -> int:
    clone_game = get_game(game_id)
    validate_ai_game(clone_game)
    
    if check_winner(clone_game.board) is not None:
        raise ValueError("Game is already over.")
    
    selected_algorithm = parse_algorithm(algorithm)
        
    if selected_algorithm == AlgorithmId.MINIMAX:
        column = choose_move(clone_game, parse_difficulty(difficulty), check_winner)
    elif selected_algorithm == AlgorithmId.MCTS:
        if mcts_selector is None:
            raise NotImplementedError("MCTS is not integrated yet.")
        column = mcts_selector(clone_game, difficulty)
    else:
        raise ValueError("Invalid algorithm.")
    
    #Shared validation for all algorithms
    validate_ai_move(clone_game, column)
    
    return column

def validate_ai_game(game: GameState | None) -> None:
    if game is None:
        raise KeyError("Game couldn't be found")
    
    if game.current_player != PLAYER_TWO:
        raise ValueError("It is not the AI player's turn")
    
    if not game.get_valid_moves():
        raise ValueError("No available moves.")
    
def validate_ai_move(game: GameState, column: int) -> None:
    if type(column) is not int:
        raise ValueError("Invalid data type selected by AI.")
    if column not in game.get_valid_moves():
        raise ValueError("Invalid Column Selected by AI.")