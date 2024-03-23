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
import random
import sys
import argparse
import psutil
import timeit
import gc
import numpy as np

sys.path.append('../cpmpy')

from cpmpy import *
from prettytable import PrettyTable

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

    nb_iterations = 10

    tablesp_ortools =  PrettyTable(['Number of Queens', 'Number of Solutions', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Overall Memory Usage (Bytes)'])
    tablesp_ortools.title = 'Results of the N-Queens problem without CSE'
    tablesp_ortools_CSE =  PrettyTable(['Number of Queens', 'Number of Solutions', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Overall Memory Usage (Bytes)'])
    tablesp_ortools_CSE.title = 'Results of the N-Queens problem with CSE' 
    tablesp_ortools_factor =  PrettyTable(['Number of Queens', 'Number of Solutions', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Overall Memory Usage (Bytes)'])
    tablesp_ortools_factor.title = 'Results of the N-Queens problem'   

    for nb in range(100, 151, 5):

        # Set a random seed for reproducibility reasons
        random.seed(0)

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
            return model.solve(solver=slvr), model_creation_time
            
        for slvr in ["z3", "z3_2"]:
            
            # Set random seed for same random conditions in both iterations
            random.seed(0)

            total_model_creation_time = []
            total_transform_time = []
            total_solve_time = []
            total_execution_time = []
            total_mem_usage = []

            for lp in range(nb_iterations):
                # Disable garbage collection for timing measurements
                gc.disable()

                initial_memory = psutil.Process().memory_info().rss
                start_time = timeit.default_timer()

                (n_sols, transform_time, solve_time), model_creation_time = run_code(slvr)
                
                execution_time = timeit.default_timer() - start_time
                memory_usage = psutil.Process().memory_info().rss - initial_memory

                total_model_creation_time.append(model_creation_time)
                total_transform_time.append(transform_time)
                total_solve_time.append(solve_time)
                total_execution_time.append(execution_time)
                total_mem_usage.append(memory_usage)

                # Re-enable garbage collection
                gc.enable()

            if slvr == 'z3':
                average_model_creation_time = sum(total_model_creation_time) / nb_iterations 
                average_transform_time = sum(total_transform_time) / nb_iterations
                average_solve_time = sum(total_solve_time) / nb_iterations 
                average_execution_time = sum(total_execution_time) / nb_iterations 
                average_mem_usage = sum(total_mem_usage) / nb_iterations

                tablesp_ortools.add_row([nb, n_sols, average_model_creation_time, average_transform_time, average_solve_time, average_execution_time, average_mem_usage])
                with open("cpmpy/timing_results/n_queens_z3.txt", "w") as f:
                    f.write(str(tablesp_ortools))
                    f.write("\n")
            elif slvr == 'z3_2':
                average_model_creation_time_2 = sum(total_model_creation_time) / nb_iterations
                average_transform_time_2 = sum(total_transform_time) / nb_iterations
                average_solve_time_2 = sum(total_solve_time) / nb_iterations
                average_execution_time_2 = sum(total_execution_time) / nb_iterations 
                average_mem_usage_2 = sum(total_mem_usage) / nb_iterations

                tablesp_ortools_CSE.add_row([nb, n_sols, average_model_creation_time_2, average_transform_time_2, average_solve_time_2, average_execution_time_2, average_mem_usage_2])
                with open("cpmpy/timing_results/n_queens_z3_CSE.txt", "w") as f:
                    f.write(str(tablesp_ortools_CSE))
                    f.write("\n")

                factor_model_creation_time = average_model_creation_time / average_model_creation_time_2
                factor_tranform_time = average_transform_time / average_transform_time_2
                factor_solve_time = average_solve_time / average_solve_time_2
                factor_execution_time = average_execution_time / average_execution_time_2
                factor_mem_usage = average_mem_usage / average_mem_usage_2

                tablesp_ortools_factor.add_row([nb, n_sols, factor_model_creation_time, factor_tranform_time, factor_solve_time, factor_execution_time, factor_mem_usage])
                with open("cpmpy/CSE_results/n_queens_z3.txt", "w") as f:
                    f.write(str(tablesp_ortools_factor))
                    f.write("\n")