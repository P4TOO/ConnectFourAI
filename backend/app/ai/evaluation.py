from app.game.board import GameState, EMPTY, PLAYER_ONE, PLAYER_TWO

#Assign score to four consecutive cells
def evaluate_window(cells: list[int], ai_player: int, playable_threat: bool = False) -> int:
    # Determine opponent
    if ai_player == PLAYER_ONE:
        opponent_player = PLAYER_TWO
    else:
        opponent_player = PLAYER_ONE
    
    # Count pieces in the window
    ai_count = cells.count(ai_player)
    opponent_count = cells.count(opponent_player)
    empty_count = cells.count(EMPTY)       

    # Evaluate AI opportunities
    if ai_count == 4:
        return 1000
    elif ai_count == 3 and empty_count == 1:
        if playable_threat:
            return 200
        return 100
    elif ai_count == 2 and empty_count == 2:
        return 10
    elif ai_count == 1 and empty_count == 3:
        return 1

    # Evaluate opponent opportunities
    elif opponent_count == 4:
        return -1000
    elif opponent_count == 3 and empty_count == 1:
        if playable_threat:
            return -300
        return -150
    elif opponent_count == 2 and empty_count == 2:
        return -10
    elif opponent_count == 1 and empty_count == 3:
        return -1

    return 0

#Find all possible four cell windows and add their scores
def evaluate_board(game: GameState, ai_player: int) -> int:
    board = game.board
    total_score = 0
    
    # Determine opponent
    if ai_player == PLAYER_ONE:
        opponent_player = PLAYER_TWO
    else:
        opponent_player = PLAYER_ONE
        
    #Precompute playable position
    playable_positions = set()
    
    for column in range(7):
        for row in range (5, -1, -1):
            if is_playable(board, row, column):
                playable_positions.add((row, column))
                break
    
    #Horizontal windows
    for row in range(6):
        for column in range(4):
            window = [
                board[row][column],
                board[row][column + 1],
                board[row][column + 2],
                board[row][column + 3]
            ]
            
            positions = [
                (row, column),
                (row, column + 1),
                (row, column + 2),
                (row, column + 3)
            ]
            
            playable_threat = False
            
            if window.count(EMPTY) == 1 and (
                window.count(ai_player) == 3
                or window.count(opponent_player) == 3
            ):
                empty_index = window.index(EMPTY)
                playable_threat = (
                    positions[empty_index] in playable_positions
                )
            
            score = evaluate_window(window, ai_player, playable_threat)
            total_score += score
    
    #Vertical windows
    for column in range(7):
        for row in range(3):
            window = [
                board[row][column],
                board[row + 1][column],
                board[row + 2][column],
                board[row + 3][column]
            ]
            
            positions = [
                (row, column),
                (row + 1, column),
                (row + 2, column),
                (row + 3, column)
            ]
            
            playable_threat = False
            
            if window.count(EMPTY) == 1 and (
                window.count(ai_player) == 3
                or window.count(opponent_player) == 3
            ):
                empty_index = window.index(EMPTY)
                playable_threat = (
                    positions[empty_index] in playable_positions
                )
            
            score = evaluate_window(window, ai_player, playable_threat)
            total_score += score
    
    #Diagonal Top Left Corner to Bottom Right Corner
    for row in range(3):
        for column in range(4):
            window = [
                board[row][column],
                board[row + 1][column + 1],
                board[row + 2][column + 2],
                board[row + 3][column + 3]
            ]
            
            positions = [
                (row, column),
                (row + 1, column + 1),
                (row + 2, column + 2),
                (row + 3, column + 3)
            ]
            
            playable_threat = False
            
            if window.count(EMPTY) == 1 and (
                window.count(ai_player) == 3
                or window.count(opponent_player) == 3
            ):
                empty_index = window.index(EMPTY)
                playable_threat = (
                    positions[empty_index] in playable_positions
                )
            
            score = evaluate_window(window, ai_player, playable_threat)
            total_score += score
            
    #Diagonal Bottom Left Corner to Top Right Corner
    for row in range(3):
        for column in range(4):
            window = [
                board[row + 3][column],
                board[row + 2][column + 1],
                board[row + 1][column + 2],                    
                board[row][column + 3]
            ]
            
            positions = [
                (row + 3, column),
                (row + 2, column + 1),
                (row + 1, column + 2),
                (row, column + 3)
            ]
            
            playable_threat = False
            if window.count(EMPTY) == 1 and (
                window.count(ai_player) == 3
                or window.count(opponent_player) == 3
            ):
                empty_index = window.index(EMPTY)
                playable_threat = (
                    positions[empty_index] in playable_positions
                )
                
            score = evaluate_window(window, ai_player, playable_threat)
            total_score += score
            
    #Add bonus points for center column
    for row in range(6):
        if board[row][3] == ai_player:
            total_score += 6
        elif board[row][3] == opponent_player:
            total_score -= 6
            
    return total_score

def is_playable(board: list[list[int]], row: int, column: int) -> bool:
    if board[row][column] == EMPTY:  
        if row == 5:
            return True
        elif board[row + 1][column] != EMPTY:
            return True
    
    return False

            