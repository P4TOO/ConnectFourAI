from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["API"])


@router.get("/ping")
def ping():
    """Verify API communication."""
    return {"message": "ConnectFourAI API connected"}
