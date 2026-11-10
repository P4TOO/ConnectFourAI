from enum import IntEnum

class Difficulty(IntEnum):
    EASY = 2
    MEDIUM = 4
    HARD = 6
    
def parse_difficulty(difficulty: str) -> Difficulty:
    difficulty = difficulty.strip().upper()
    
    if difficulty == "EASY":
        return Difficulty.EASY
    elif difficulty == "MEDIUM":
        return Difficulty.MEDIUM
    elif difficulty == "HARD":
        return Difficulty.HARD
    
    raise ValueError("Invalid difficulty level.")