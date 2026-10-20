
from typing import Literal

from pydantic import BaseModel, Field

Board = list[list[int]]


class GameCreateRequest(BaseModel):
    algorithm: Literal["minimax", "mcts", "random"] = "minimax"
    difficulty: Literal["easy", "medium", "hard"] = "medium"


class MoveRequest(BaseModel):
    column: int = Field(ge=0, le=6)


class MoveInfo(BaseModel):
    row: int
    column: int
    player: int


class GameStateResponse(BaseModel):
    game_id: str
    board: Board
    current_player: int | None
    status: Literal["ongoing", "win", "draw"]
    winner: int | None = None
    last_move: MoveInfo | None = None


class AIMetrics(BaseModel):
    decision_time_ms: float
    nodes_explored: int | None = None
    simulations_run: int | None = None


class AIMoveResponse(GameStateResponse):
    metrics: AIMetrics
