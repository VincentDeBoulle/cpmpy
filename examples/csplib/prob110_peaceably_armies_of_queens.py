"""
Peaceably co-existing armies of queens in CPMpy

CSPlib prob110
https://www.csplib.org/Problems/prob110/

Problem description from CSPlib website:
In the "Armies of queens" problem, we are required to place two equal-sized armies
of black and white queens on a chessboard so that the white queens do not attack
the black queens (and necessarily visa versa) and to find the maximum size of the
two armies.

This CPMpy model was written by Vincent De Boulle
"""
# Load the libraries
from cpmpy import *

def peaceable_queens(n=8):

    b = intvar(0, 1, shape=(n,n))
    w = intvar(0, 1, shape=(n,n))

    model = Model()

    num_black_queens = sum(b)
    num_white_queens = sum(w)

    model += (num_black_queens == num_white_queens)
    model.objective(num_black_queens, minimize=False)

    for bx in range(n):
        for by in range(n):
            for wx in range(n):
                for wy in range(n):
                    if (bx, by)  == (wx, wy):
                        model += b[bx][by] + w[wx][wy] <= 1
                    if bx < wx or (bx == wx and by < wy):
                        if bx == wx or by == wy or abs(bx - wx) == abs(by - wy):
                            model += b[bx][by] + w[wx][wy] <= 1
                            model += w[bx][by] + b[wx][wy] <= 1
    return model, b, w

if __name__ == "__main__":
    n = 7 # Size of the board
    print('Size: ', n)
    
    model, black_queens, white_queens = peaceable_queens(n)

    if model.solve():
        line = '+---'*n +'+\n'
        out = line
        for x in range(n):
            for y in range(n):
                if black_queens.value()[x][y] == 1:
                    out += '| B '
                elif white_queens.value()[x][y] == 1:
                    out += '| W '
                else:
                    out += '|   '
            out += '|\n' + line
        print(out)
    else:
        print("Model is unsatisfiable")

