import tkinter as tk
import tkinter.messagebox as messagebox
import random
import copy

rows, cols = 6, 7  # The board's dimensions

board = [[' ' for _ in range(cols)] for _ in range(rows)]  # We're now instantiating a game board or 2D list comprised of empty spaces

def move_and_check_win(board, col, player):  # Simultaneously placing a token and checking if the placement results in a win
    for row in range(rows - 1, -1, -1):  # Check starts at the bottom row
        if board[row][col] == ' ':  # Locate the first available space
            board[row][col] = player  # Subsequently place the player's token in that space
            if check_win(board, player, row, col):  # Second part, using the code a few lines down, is the move a 'royal flush', 'buzzbeater', 'gold medal', etc?
                return row, True
            return row, False
    return None, False  # Stop the move if the column is already full

def check_win(board, player, r, c):  # Check all possible win scenarios
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # Establishing the directions of possible win scenarios
    
    for dr, dc in directions:
        count = 1
        
        for i in range(1, 4):  # Checking scenarios in the positive direction
            nr, nc = r + dr * i, c + dc * i
            if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] == player:
                count += 1
            else:
                break
        # Check in the negative direction
        for i in range(1, 4):
            nr, nc = r - dr * i, c - dc * i
            if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] == player:
                count += 1
            else:
                break
        if count >= 4:  # win scenario identified
            return True
    return False  # no scenarios identified

def evaluate_board(board, player):  # Creating a scoring system to govern how the AI determines which space to place its token in

    opponent = 'X' if player == 'O' else 'O'  
    score = 0

    center_array = [board[r][cols // 2] for r in range(rows)]  # Adding value to available space in the center of the board which reflects real-world strategy
    center_count = center_array.count(player)
    score += center_count * 3

    def evaluate_combo(combo):  # Check how many of the player's tokens there are in a row and whether there's a blockable win scenario for the opponent and return a score to guide it in its decision-making
        if combo.count(player) == 4:
            return 100  # Winning move
        elif combo.count(player) == 3 and combo.count(' ') == 1:
            return 10  # Almost winning
        elif combo.count(player) == 2 and combo.count(' ') == 2:
            return 5  # Good positioning
        elif combo.count(opponent) == 3 and combo.count(' ') == 1:
            return -15  # Block opponent's win
        return 0

    # Horizontal combos
    for row in range(rows):
        for col in range(cols - 3):
            combo = board[row][col:col + 4]
            score += evaluate_combo(combo)

    # Vertical combos
    for row in range(rows - 3):
        for col in range(cols):
            combo = [board[row + i][col] for i in range(4)]
            score += evaluate_combo(combo)

    # Diagonal combos in the positive direction
    for row in range(rows - 3):
        for col in range(cols - 3):
            combo = [board[row + i][col + i] for i in range(4)]
            score += evaluate_combo(combo)

    # Diagonal (/) combos in the negative direction
    for row in range(3, rows):
        for col in range(cols - 3):
            combo = [board[row - i][col + i] for i in range(4)]
            score += evaluate_combo(combo)

    return score 

def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_columns = get_valid_columns(board)  # Get all valid locations for a move
    random.shuffle(valid_columns)  # Introduce randomness to the move selection
    is_terminal = is_terminal_node(board)  # Check if the game is over


    if depth == 0 or is_terminal:
        if is_terminal:
            if check_win(board, 'O'):  # AI wins
                return None, 100000000
            elif check_win(board, 'X'):  # Player wins
                return None, -100000000
            else:  # No more valid moves
                return None, 0
        else:  # Depth is 0
            return None, evaluate_board(board, 'O')

    if maximizingPlayer:
        value = float('-inf')
        best_col = random.choice(valid_columns)
        for col in valid_columns:
            temp_board = copy.deepcopy(board)  
            row, _ = move_and_check_win(temp_board, col, 'O')
            new_score = minimax(temp_board, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                best_col = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return best_col, value

    else:  # Minimizing player
        value = float('inf')
        best_col = random.choice(valid_columns)
        for col in valid_columns:
            temp_board = copy.deepcopy(board)  
            row, _ = move_and_check_win(temp_board, col, 'X')
            new_score = minimax(temp_board, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                best_col = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return best_col, value

def get_valid_columns(board):
    return [c for c in range(cols) if board[0][c] == ' ']  # Returns all columns that are not full

def is_terminal_node(board):
    return check_win(board, 'X', 0, 0) or check_win(board, 'O', 0, 0) or len(get_valid_columns(board)) == 0

def ai_turn(root):  # Executes AI's turn based on minimax algorithm
    col, _ = minimax(board, 3, -300, 300, True)
    row, _ = move_and_check_win(board, col, 'O')
    refresh_board(root)
    if check_win(board, 'O', row, col):
        messagebox.showinfo("Mission Failed", "HAL 9000 wins! Humanity goes home devastated")
        root.quit()  # End the game

def refresh_board(root):

    for row in range(rows):
        for col in range(cols):
            color = 'black'  
            if board[row][col] == 'X':  # Human player's token
                color = 'red'
            elif board[row][col] == 'O':  # AI's token
                color = 'yellow'
            root.grid_slaves(row=row, column=col)[0].config(bg=color)  

def start_game():

    root = tk.Tk()
    root.title("Olympic Connect 4")

    starting_player = random.choice(['X', 'O'])  # randomly pick which player starts given the advantage

    for row in range(rows):  # Label creation for the board
        for col in range(cols):
            lbl = tk.Label(root, text=" ", bg="white", width=9, height=4, relief="sunken", borderwidth=1)
            lbl.grid(row=row, column=col, padx=2, pady=2)
            lbl.bind("<Button-1>", lambda e, c=col: human_play(root, c))  # Bind mouse clicks as a human playing the game

    if starting_player == 'O':  # AI plays first
        ai_turn(root)

    root.mainloop()

def human_play(root, col):  # Allows player to make their move
    if board[0][col] == ' ':
        row, player_wins = move_and_check_win(board, col, 'X')
        refresh_board(root)
        if player_wins:
            messagebox.showinfo("Mission Failed", "You win the gold medal! May your victory be immortalized!")
            root.quit()
        else:
            ai_turn(root)

if __name__ == "__main__":
    start_game()
