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

    nb_iterations = 10

    tablesp_ortools =  PrettyTable(['Number of Queens', 'Number of Solutions', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'number of search branches'])
    tablesp_ortools.title = f'Results of the N-Queens problem without CSE (average of {nb_iterations} iterations)'
    tablesp_ortools_CSE =  PrettyTable(['Number of Queens', 'Number of Solutions', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'number of search branches'])
    tablesp_ortools_CSE.title = f'Results of the N-Queens problem with CSE (average of {nb_iterations} iterations)'    

    for nb in range(500, 700, 5):
        parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("-n", type=int, default=nb, help="Number of queens")
        parser.add_argument("--solution_limit", type=int, default=0, help="Number of solutions, find all by default")

        args = parser.parse_args()
        
        def run_code(slvr):
            start_model_time = timeit.default_timer()
            model, (queens,) = n_queens(args.n)
            model_creation_time = timeit.default_timer() - start_model_time
            #n_sols = model.solveAll(solution_limit=args.solution_limit, display=lambda: print_sol(queens))
            print("queens:{}".format(args.n))
            return model.solve(), model_creation_time
            
        for slvr in ["ortools"]:
            total_model_creation_time = []
            total_transform_time = []
            total_solve_time = []
            total_execution_time = []
            total_num_branches = []

            for lp in range(nb_iterations):
                # Disable garbage collection for timing measurements
                gc.disable()

                # Measure the model creation and execution time
                start_time = timeit.default_timer()
                (n_sols, transform_time, solve_time, num_branches), model_creation_time = run_code(slvr)
                execution_time = timeit.default_timer() - start_time

                total_model_creation_time.append(model_creation_time)
                total_transform_time.append(transform_time)
                total_solve_time.append(solve_time)
                total_execution_time.append(execution_time)
                total_num_branches.append(num_branches)

                # Re-enable garbage collection
                gc.enable()
            
            average_model_creation_time = sum(sorted(total_model_creation_time)[:3]) / 3 
            average_transform_time = sum(sorted(total_transform_time)[:3]) / 3 
            average_solve_time = sum(sorted(total_solve_time)[:3]) / 3 
            average_execution_time = sum(sorted(total_execution_time)[:3]) / 3 
            average_num_branches = sum(sorted(total_num_branches)[:3]) / 3

            if slvr == 'ortools':
                tablesp_ortools.add_row([nb, n_sols, average_model_creation_time, average_transform_time, average_solve_time, average_execution_time, average_num_branches])
                with open("cpmpy/timing_results/n_queens.txt", "w") as f:
                    f.write(str(tablesp_ortools))
                    f.write("\n")
            elif slvr == 'ortools_CSE':
                tablesp_ortools_CSE.add_row([nb, n_sols, average_model_creation_time, average_transform_time, average_solve_time, average_execution_time, average_num_branches])
                with open("cpmpy/timing_results/n_queens_CSE.txt", "w") as f:
                    f.write(str(tablesp_ortools_CSE))
                    f.write("\n")
