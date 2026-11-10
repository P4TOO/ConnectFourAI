from collections.abc import Callable

from fastapi import APIRouter, Depends, HTTPException

from app.api.schemas import (
    AIMoveRequest,
    GameStateResponse,
    MoveRequest,
    MoveInfo,
)
from app.services.game_service import (
    create_game,
    get_game,
    apply_player_move,
    get_ai_move,
)

router = APIRouter(prefix="/api/games", tags=["Games"])

def get_winner_checker() -> Callable:
    raise HTTPException(
        status_code=503,
        detail="Winner checking is not integrated yet.",
    )
    
def get_mcts_selector() -> Callable | None:
    """Return the MCTS implementation when available."""
    return None
    
def build_response(game_id, game):
    """Convert a GameState into an API response."""
    return GameStateResponse(
        game_id=game_id,
        board=game.board,
        current_player=game.current_player,
        status="ongoing",
        winner=None,
        last_move=None,
    )


@router.post("", response_model=GameStateResponse, status_code=201)
def create_game_endpoint():
    game_id, game = create_game()
    return build_response(game_id, game)


@router.get("/{game_id}", response_model=GameStateResponse)
def get_game_endpoint(game_id: str):
    game = get_game(game_id)

    if game is None:
        raise HTTPException(
            status_code=404,
            detail="Game not found",
        )

    return build_response(game_id, game)


@router.post(
    "/{game_id}/moves",
    response_model=GameStateResponse,
)
def player_move_endpoint(game_id: str, request: MoveRequest):
    try:
        game, row = apply_player_move(
            game_id, request.column
        )

    except KeyError:
        raise HTTPException(
            status_code=404,
            detail="Game not found",
        ) from None

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from None

    response = build_response(game_id, game)

    response.last_move = MoveInfo(
        row=row,
        column=request.column,
        player=1,
    )

    return response

@router.post("/{game_id}/ai-move")
def ai_move_endpoint(
    game_id: str,
    request: AIMoveRequest,
    check_winner: Callable = Depends(get_winner_checker),
    mcts_selector: Callable | None = Depends(get_mcts_selector),
):
    try:
        column = get_ai_move(
            game_id,
            request.algorithm,
            request.difficulty,
            check_winner,
            mcts_selector=mcts_selector,
        )

    except KeyError:
        raise HTTPException(
            status_code=404,
            detail="Game not found",
        ) from None

    except NotImplementedError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from None

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from None

    return {"column": column}