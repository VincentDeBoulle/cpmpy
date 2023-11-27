"""
Peg Solitaire Problem

CSPlib: https://www.csplib.org/Problems/prob037/
"""

import sys
sys.path.append('../cpmpy')

from cpmpy import *
from prob037b_peg_solitaire_boards import generate_boards
import pprint

def peg_solitaire():
    origin_x, origin_y, nMoves = [3, 3, 0]

    init_board, final_board = generate_boards(origin_x, origin_y)

    #pprint.pprint(init_board)
    #pprint.pprint(final_board)

    n, m = len(init_board), len(init_board[0])

    horizon = sum(sum(v for v in row if v != 2) for row in init_board) - sum(sum(v for v in row if v != 2) for row in final_board)
    nMoves = horizon if nMoves <= 0 or horizon < nMoves else nMoves
    assert 0 < nMoves <= horizon

    pairs = [(i, j) for i in range(n) for j in range(m) if init_board[i][j] != 2]
    
    def build_transitions(board):
        t = []
        for i, j in pairs:
            if i + 2 < n and board[i + 2][j] != 2:
                t.append((i, j, i + 1, j, i + 2, j))
            if j + 2 < m and board[i][j + 2] != 2:
                t.append((i, j, i, j + 1, i, j + 2))
            if i - 2 >= 0 and board[i - 2][j] != 2:
                t.append((i, j, i - 1, j, i - 2, j))
            if j - 2 >= 0 and board[i][j - 2] != 2:
                t.append((i, j, i, j - 1, i, j - 2))
        return sorted(t)

    transitions = build_transitions(init_board)
    nTransitions = len(transitions)

    # x[t,i,j] is the value at row i and column j at time t
    x = intvar(0, 2, shape=(nMoves+1, n, m))

    for t in range(nMoves + 1):
        for i in range(n):
            for j in range(m):
                x[t, i, j] = 2 if init_board[i][j] == 2 else intvar(0,1)
    
    # y[t] is the move (transition) performed at time t
    y = intvar(0, nTransitions, shape=nMoves)

    # Create a CPM model
    model = Model()

    # setting the initial board
    model += x[0] == init_board

    # setting the final board
    model += x[-1] == final_board

    def unchanged(i, j, t):
        valid = [k for k, tr in enumerate(transitions) if (i, j) in (tr[0:2], tr[2:4], tr[4:6])] # position (i, j) is one of the three pairs of this transition
        if len(valid) == 0:
            return True
        return x[t, i, j] == x[t + 1, i, j] if all(y[t] != k for k in valid) else True
    def to0(i, j, t):
        valid = [k for k, tr in enumerate(transitions) if (i, j) in (tr[0:2], tr[2:4])]
        if len(valid) == 0:
            return True
        return (x[t, i, j] == 1) & (x[t + 1, i, j] == 0) if any(y[t] == k for k in valid) else True
    def to1(i, j, t):
        valid = [k for k, tr in enumerate(transitions) if (i, j) == tr[4:6]]
        if len(valid) == 0:
            return True
        return (x[t, i, j] == 0) & (x[t + 1, i, j] == 1) if any(y[t] == k for k in valid) else True
    
    for (i, j) in pairs:
        for t in range(nMoves):
            model += unchanged(i, j, t)
            model += to0(i, j, t)
            model += to1(i, j, t)

    return model, x,y

if __name__ == "__main__":
    model,x,y = peg_solitaire()
    model.solve()
    #print(model)
    y_values = []
    for i in y:
        y_values.append(i.value())
    print("y_values: ", y_values)
    
    for m in range(len(x)): 
        line = '+---'*7 +'+\n'
        out = line       
        for i in range(len(x[m][0])):
            for j in range(len(x[0][0])):
                if type(x[m][i][j]) != int:
                    v = x[m][i][j].value()
                    if v == 1:
                        out += ' p  '
                    elif v == 0:
                        out += ' o  '
                    else:
                        out += ' x  '
                else:
                    out += '|   '
            out += '|\n' + line
        print(out)
