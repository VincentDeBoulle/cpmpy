"""
Peaceably co-existing armies of queens in CPMpy

CSPlib prob110
https://www.csplib.org/Problems/prob110/models/PeacableArmies.py.html

Problem description from previous website:
In the "Armies of queens" problem, we are required to place two equal-sized armies
of black and white queens on a chessboard so that the white queens do not attack
the black queens (and necessarily visa versa) and to find the maximum size of the
two armies.

This CPMpy model was written by Vincent De Boulle
"""
# Add the correct path
import sys
sys.path.append('../cpmpy')

# Load the libraries
import numpy as np
from cpmpy import *
import timeit
from prettytable import PrettyTable
import gc

def peaceable_queens(n=6):

    # x[i][j] is 1 (resp., 2), if a black (resp., white) queen is in the cell at row i
    # and column j. It is 0 otherwise.
    queens = intvar(0,2, shape=(n,n))

    model = Model(maximize=n)

    def different(i1, j1, i2, j2):
        return queens[i1][j1] + queens[i2][j2] != 3
            
    # No two opponent queens can attack each other
    for i1 in range(n):
        for j1 in range(n):
            for i2 in range(n):
                for j2 in range(n):
                    model += different(i1, j1, i2, j2)
 
    # Counting the number of black and white queens
    black_queen_count = sum([queens[i, j] == 1 for i in range(n) for j in range(n)])
    white_queen_count = sum([queens[i, j] == 2 for i in range(n) for j in range(n)])

    model += black_queen_count == white_queen_count

    return model

if __name__ == "__main__":
    import argparse

    tablesp = PrettyTable(['Size of board', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'number of search branches'])

    for nb in range(10, 20):
        parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("-n", type=int, default=nb, help="Size of the board")

        args = parser.parse_args()

        def run_code():
            start_model_time = timeit.default_timer()
            model = peaceable_queens(args.n)
            model_creation_time = timeit.default_timer() - start_model_time
            print("Size:{}".format(args.n))
            return model.solve(), model_creation_time
            

        # Disable garbage collection for timing measurements
        gc.disable()

        # Measure the model creation and execution time
        start_time = timeit.default_timer()
        (_, transform_time, solve_time, num_branches), model_creation_time = run_code()
        execution_time = timeit.default_timer() - start_time

        # Re-enable garbage collection
        gc.enable()

        tablesp.add_row([nb, model_creation_time, transform_time, solve_time, execution_time, num_branches])

        with open("cpmpy/timing_results/peaceable_queens.txt", "w") as f:
            f.write(str(tablesp))
            f.write("\n")

        