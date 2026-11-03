
from collections.abc import Callable

from app.game.board import GameState, PLAYER_ONE, PLAYER_TWO

#Evaluate score of gamestate (Rewarding & Punishment) called in both player and AI turn
def minimax(simulated_game: GameState, depth: int, ai_player: int, check_winner: Callable) -> int:
    winner = check_winner(simulated_game.board)
    
    if winner is not None:   
        #AI wins 
        if winner == ai_player:
            return 1000
        #Player wins
        elif winner != ai_player:
            return -1000
        
    #Get available columns
    available_columns = simulated_game.get_valid_moves()
        
    #All columns are full
    if len(available_columns) == 0:
        return 0
    
    #Depth reaches zero
    if depth == 0:
        return 0
    
    if simulated_game.current_player == ai_player:
        best_score = float("-inf")
    else:
        best_score = float("inf")
    
    #Select available column
    for column in available_columns:
        #Create copy of game
        clone_game = simulated_game.clone()
        
        #Simulate move
        clone_game.apply_move(column)
        
        score = minimax(clone_game, depth - 1, ai_player, check_winner)
        
        if simulated_game.current_player == ai_player:
            best_score = max(score, best_score)
        else:
            best_score = min(score, best_score)
            
    return best_score

#Find the best move the AI can make (Called only during AI turn)
def choose_move(game: GameState, depth: int, check_winner: Callable) -> int:
    winner = check_winner(game.board)
    
    if winner is not None:   
        raise ValueError("Game is already over.")
    
    #Get all available columns
    available_columns = game.get_valid_moves()
    
    if len(available_columns) == 0:
        raise ValueError("No available moves.")
    
    if depth <= 0:
        raise ValueError("Depth must be greater than zero.")
    
    best_score = float("-inf")
    best_column = -1
    ai_player = game.current_player
    
    for column in available_columns:
        #Create copy of game
        clone_game = game.clone()
        
        #Simulate move
        clone_game.apply_move(column)
        
        score = minimax(clone_game, depth - 1, ai_player, check_winner)
        
        if score > best_score:
            best_column = column
            best_score = score
    
    return best_column
        
        
        