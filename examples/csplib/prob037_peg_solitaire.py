import array
import sys
sys.path.append('../cpmpy')

import timeit
from prettytable import PrettyTable
from cpmpy import *
import gc
from examples.csplib.prob037b_peg_solitaire_boards import generate_boards

def peg_solitaire(variant):
    assert variant in {"english", "3x3", "4x4", "french", "test1", "test2"}

    origin_x, origin_y, nMoves = [3, 3, 0]

    init_board, final_board = generate_boards(variant, origin_x, origin_y)

    n, m = len(init_board), len(init_board[0])

    horizon = sum(sum(v for v in row if v) for row in init_board) - sum(sum(v for v in row if v) for row in final_board)
    nMoves = int(horizon if nMoves <= 0 or horizon < nMoves else nMoves)
    assert 0 < nMoves <= horizon

    pairs = [(i, j) for i in range(n) for j in range(m) if init_board[i][j] is not None]

    def build_transitions(board):
        t = []
        for i, j in pairs:
            if i + 2 < n and board[i + 2][j] is not None:
                t.append((i, j, i + 1, j, i + 2, j))
            if j + 2 < m and board[i][j + 2] is not None:
                t.append((i, j, i, j + 1, i, j + 2))
            if i - 2 >= 0 and board[i - 2][j] is not None:
                t.append((i, j, i - 1, j, i - 2, j))
            if j - 2 >= 0 and board[i][j - 2] is not None:
                t.append((i, j, i, j - 1, i, j - 2))
        return sorted(t)

    transitions = build_transitions(init_board)
    nTransitions = len(transitions)

    # Create a CPM model
    model = Model()

    # Create variables and domains
    x = intvar(0, 1, shape=(nMoves + 1, n, m))
    y = intvar(0, nTransitions, shape=nMoves)

    # Set initial and final board
    model += (x[0] == init_board)
    model += (x[nMoves] == final_board)

    # Define helper functions
    def unchanged(i, j, t, model):
        valid = [k for k, tr in enumerate(transitions) if (i, j) in (tr[0:2], tr[2:4], tr[4:6])]
        model += (sum(y[t] != k for k in valid) == len(valid)) & (x[t, i, j] == x[t + 1, i, j])

    def to0(i, j, t, model):
        valid = [k for k, tr in enumerate(transitions) if (i, j) in (tr[0:2], tr[2:4])]
        model += (sum(y[t] != k for k in valid) == len(valid)) & (x[t, i, j] == 1) & (x[t + 1, i, j] == 0)

    def to1(i, j, t, model):
        valid = [k for k, tr in enumerate(transitions) if (i, j) == tr[4:6]]
        model += (sum(y[t] != k for k in valid) == len(valid)) & (x[t, i, j] == 0) & (x[t + 1, i, j] == 1)


    # Add constraints
    for i, j in pairs:
        for t in range(nMoves):
            unchanged(i, j, t, model)
            to0(i, j, t, model)
            to1(i, j, t, model)

    print(model)

    # Solve the model
    print(model.solve())

if __name__ == "__main__":
    peg_solitaire("english")
