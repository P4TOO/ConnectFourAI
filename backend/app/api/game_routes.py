from fastapi import APIRouter, HTTPException

from app.api.schemas import GameStateResponse, MoveRequest, MoveInfo
from app.services.game_service import create_game, get_game, apply_player_move

router = APIRouter(prefix="/api/games", tags=["Games"])


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
