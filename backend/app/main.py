
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router as api_router
from app.api.game_routes import router as game_router

app = FastAPI(
    title="Connect Four vs. AI API",
    description="Python backend for Connect Four game logic and AI algorithms.",
    version="0.1.0",
)

# Allow our React frontend to communicate with FastAPI.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(game_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
