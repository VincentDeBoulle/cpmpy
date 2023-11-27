def reverse_board(board):
    return [[0 if board[i][j] == 1 else 1 if board[i][j] == 0 else 2 for i in range(len(board))] for j in range(len(board[0]))]

def english_board(i=3, j=3):
    init_board = [
        [2, 2, 1, 1, 1, 2, 2],
        [2, 2, 1, 1, 1, 2, 2],
        [1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1],
        [2, 2, 1, 1, 1, 2, 2],
        [2, 2, 1, 1, 1, 2, 2]
    ]
    init_board[i][j] = 0
    return init_board, reverse_board(init_board)

def generate_boards(origin_x, origin_y):
    return english_board(origin_x, origin_y)