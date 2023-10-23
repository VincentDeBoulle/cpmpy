"""
N-queens problem in CPMpy

CSPlib prob054

Problem description from the numberjack example:
The N-Queens problem is the problem of placing N queens on an N x N chess
board such that no two queens are attacking each other. A queen is attacking
another if it they are on the same row, same column, or same diagonal.

Here are some different approaches with different version of both
the constraints and how to solve and print all solutions.


This CPMpy model was written by Hakan Kjellerstrand (hakank@gmail.com)
See also my CPMpy page: http://hakank.org/cpmpy/

Modified by Ignace Bleukx
"""
import sys
sys.path.append('../cpmpy')

# load the libraries
import numpy as np
from cpmpy import *
import timeit
from prettytable import PrettyTable
import gc

def n_queens(n=16):

    queens = intvar(1, n, shape=n)

    # Constraints on columns and left/right diagonal
    model = Model([
        AllDifferent(queens),
        AllDifferent(queens - np.arange(n)),
        AllDifferent(queens + np.arange(n)),
    ])

    return model, (queens,)

def print_sol(queens):
    queens = queens.value()
    board = np.zeros(shape=(len(queens), len(queens)), dtype=str)
    for i,q in enumerate(queens):
        board[i,q-1] = chr(0x265B)
    print(np.array2string(board,formatter={'str_kind':lambda x : x if len(x) != 0 else " "}))
    print()

if __name__ == "__main__":
    import argparse

    tablesp = PrettyTable(['Number of Queens', 'Number of Solutions', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'number of search branches'])

    for nb in range(5, 14):
        parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("-n", type=int, default=nb, help="Number of queens")
        parser.add_argument("--solution_limit", type=int, default=0, help="Number of solutions, find all by default")

        args = parser.parse_args()

        def create_model():
            return n_queens(args.n)
        
        # Define a function to run the code
        def run_code():
            start_model_time = timeit.default_timer()
            model, (queens,) = n_queens(args.n)
            model_creation_time = timeit.default_timer() - start_model_time
            #n_sols = model.solveAll(solution_limit=args.solution_limit, display=lambda: print_sol(queens))
            print("queens:{}".format(args.n))
            return model.solveAll(solution_limit=args.solution_limit), model_creation_time
            

        # Disable garbage collection for timing measurements
        gc.disable()

        # Measure the model creation and execution time
        start_time = timeit.default_timer()
        (n_sols, transform_time, solve_time, num_branches), model_creation_time = run_code()
        execution_time = timeit.default_timer() - start_time

        # Re-enable garbage collection
        gc.enable()

        tablesp.add_row([nb, n_sols, model_creation_time, transform_time, solve_time, execution_time, num_branches])

        with open("cpmpy/timing_results/n_queens_times.txt", "w") as f:
            f.write(str(tablesp))
            f.write("\n")
