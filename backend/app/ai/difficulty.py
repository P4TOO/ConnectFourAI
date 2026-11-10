from enum import IntEnum

class Difficulty(IntEnum):
    EASY = 2
    MEDIUM = 4
    HARD = 6
    
def parse_difficulty(difficulty: str) -> Difficulty:
    if difficulty.strip().upper() == "EASY":
        return Difficulty.EASY
    elif difficulty.strip().upper() == "MEDIUM":
        return Difficulty.MEDIUM
    elif difficulty.strip().upper() == "HARD":
        return Difficulty.HARD
    
    raise ValueError("Invalid difficulty level.")