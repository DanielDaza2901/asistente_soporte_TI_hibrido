WIN_LINES = ((0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6))
board = ["X", "O", "X", "O", "X", " ", " ", " ", "O"]

def winner(current_board):
    for a, b, c in WIN_LINES:
        if current_board[a] == current_board[b] == current_board[c] and current_board[a] != " ":
            return current_board[a]
    return None

def minimax(current_board, maximizing):
    w = winner(current_board)
    if w == "X": return 1
    if w == "O": return -1
    if " " not in current_board: return 0
    
    mark = "X" if maximizing else "O"
    scores = []
    
    for i, cell in enumerate(current_board):
        if cell == " ":
            nxt = current_board.copy()
            nxt[i] = mark
            scores.append(minimax(nxt, not maximizing))
            
    return max(scores) if maximizing else min(scores)

def best_move(current_board):
    choices = []
    for i, cell in enumerate(current_board):
        if cell == " ":
            nxt = current_board.copy()
            nxt[i] = "X"
            choices.append((minimax(nxt, False), i))
    return max(choices)[1]

if __name__ == "__main__":
    print("Mejor posición:", best_move(board))