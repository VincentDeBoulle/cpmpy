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

    tablesp_ortools = PrettyTable(['Size of board', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Search Branches'])
    tablesp_ortools.title = 'Results of the n queens problem with CSE (average of 10 iterations)'
    tablesp_ortools_noCSE = PrettyTable(['Size of board', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Search Branches'])
    tablesp_ortools_noCSE.title = 'Results of the n queens problem without CSE (average of 10 iterations)'

    for nb in range(20, 30):
        parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("-n", type=int, default=nb, help="Size of the board")

        args = parser.parse_args()

        def run_code():
            start_model_time = timeit.default_timer()
            model = peaceable_queens(args.n)
            model_creation_time = timeit.default_timer() - start_model_time
            print("Size:{}".format(args.n))
            return model.solve(), model_creation_time

        for slvr in ['ortools_noCSE', 'ortools']:
            total_model_creation_time = 0
            total_transform_time = 0
            total_solve_time = 0
            total_execution_time = 0
            total_num_branches = 0 

            for lp in range(10):
                # Disable garbage collection for timing measurements
                gc.disable()

                # Measure the model creation and execution time
                start_time = timeit.default_timer()
                (_, transform_time, solve_time, num_branches), model_creation_time = run_code()
                execution_time = timeit.default_timer() - start_time

                total_model_creation_time += model_creation_time
                total_transform_time += transform_time
                total_solve_time += solve_time
                total_execution_time += execution_time
                total_num_branches += num_branches
                # Re-enable garbage collection
                gc.enable()


            average_model_creation_time = total_model_creation_time / 10
            average_transform_time = total_transform_time / 10
            average_solve_time = total_solve_time / 10
            average_execution_time = total_execution_time / 10
            average_num_branches = total_num_branches / 10
            
            
            if slvr == 'ortools':
                tablesp_ortools.add_row([nb, average_model_creation_time, average_transform_time, average_solve_time, average_execution_time, average_num_branches])
                with open("cpmpy/timing_results/n_queens_CSE.txt", "w") as f:
                    f.write(str(tablesp_ortools))
                    f.write("\n")
            else:
                tablesp_ortools_noCSE.add_row([nb, average_model_creation_time, average_transform_time, average_solve_time, average_execution_time, num_branches])
                with open("cpmpy/timing_results/n_queens.txt", "w") as f:
                    f.write(str(tablesp_ortools_noCSE))
                    f.write("\n")

            