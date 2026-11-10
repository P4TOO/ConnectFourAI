from enum import StrEnum

class AlgorithmId(StrEnum):
    MINIMAX = "minimax"
    MCTS = "mcts"
    
def parse_algorithm(algorithm: str) -> AlgorithmId:
    algorithm = algorithm.strip().lower()
    
    if algorithm == "minimax":
        return AlgorithmId.MINIMAX
    elif algorithm == "mcts":
        return AlgorithmId.MCTS
    
    raise ValueError("Invalid algorithm.")