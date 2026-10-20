
from copy import deepcopy
from dataclasses import dataclass, field

ROWS = 6
COLUMNS = 7

EMPTY = 0
PLAYER_ONE = 1
PLAYER_TWO = 2


#Gives each new game an independent 6x7 array
def create_empty_board() -> list[list[int]]:
    """Create a 6x7 Connect Four board."""
    return [
        [EMPTY for _ in range(COLUMNS)]
        for _ in range(ROWS)
    ]


#Groups the board, turn, and number of moves into one object
@dataclass
class GameState:
    board: list[list[int]] = field(default_factory=create_empty_board)
    current_player: int = PLAYER_ONE
    move_count: int = 0

    #Returns columns where pieces can still be place
    def get_valid_moves(self) -> list[int]:
        """Return columns that are not full."""
        return [
            col for col in range(COLUMNS)
            if self.board[0][col] == EMPTY
        ]

    #Applies gravity automatically and switches players
    def apply_move(self, column: int) -> int:
        """
        Drop the current player's piece into a column.

        Returns the row where the piece landed.
        Raises ValueError for an invalid or full column.
        """
        if type(column) is not int or not 0 <= column < COLUMNS:
            raise ValueError("Column must be an integer from 0 to 6.")

        if column not in self.get_valid_moves():
            raise ValueError("Selected column is full.")

        for row in range(ROWS - 1, -1, -1):
            if self.board[row][column] == EMPTY:
                self.board[row][column] = self.current_player
                self.move_count += 1

                self.current_player = (
                    PLAYER_TWO
                    if self.current_player == PLAYER_ONE
                    else PLAYER_ONE
                )

                return row

        raise ValueError("No available position in column.")

    #Creates an independent copy of the current game state that the AI can manipulate without affecting the actual game
    def clone(self) -> "GameState":
        """Return an independent copy of the game state."""
        return deepcopy(self)
