"""
Diamond-free Degree Sequences in cpmpy.

CSPLib Problem 050
http://www.csplib.org/Problems/prob050/

Fill in a binary matrix of size n * n in such a way that
- For every grouping of four rows, the sum of their non-symmetrical
  values is less than or equal to 4,
- No rows contain just zeroes,
- Every row has a sum modulo 3,
- The sum of the matrix is modulo 12.
- No row R contains a 1 in its Rth column.

Note on first constraint in model:
A group of four nodes can have at most four edges between them.
Since the matrix for this model will represent the adjacency
matrix of the graph, we need to take into consideration the fact
that the matrix will be symmetrical.

This is a port of the Numberjack example DiamondfreeDegreeSequences.py:

Model created by Hakan Kjellerstrand, hakank@hakank.com
See also my cpmpy page: http://www.hakank.org/cpmpy/

Modified by Ignace Bleukx, ignace.bleukx@kuleuven.be

"""
import random
import sys
import numpy as np
import gc
import argparse
import psutil
import timeit

sys.path.append('../cpmpy')

from cpmpy import *
from cpmpy.solvers import *
from itertools import combinations
from prettytable import PrettyTable

def diamond_free(N=10):
    # By definition a and b will have the same cardinality:
    matrix = boolvar(shape=(N, N), name="matrix")

    model = Model()

    # No rows contain just zeroes.
    model += [sum(row) > 0 for row in matrix] # can be written cleaner, see issue #117
    # Every row has a sum modulo 3.
    model += [sum(row) % 3 == 0 for row in matrix]
    # The sum of the matrix is modulo 12.
    model += sum(matrix) % 12 == 0
    # No row R contains a 1 in its Rth column.
    model += [matrix[np.diag_indices(N)] == 0]

    # Every grouping of 4 rows can have at most a sum of 4 between them.
    for a, b, c, d in combinations(range(N), 4):
        model += sum([matrix[a][b], matrix[a][c], matrix[a][d],
                      matrix[b][c], matrix[b][d], matrix[c][d]]) <= 4

    # Undirected graph
    model += matrix == matrix.T

    # Symmetry breaking
    # lexicographic ordering of rows
    for r in range(N - 1):
        b = boolvar(N + 1)
        model += b[0] == 1
        model += b == ((matrix[r] <= matrix[r + 1]) &
                       ((matrix[r] < matrix[r + 1]) | b[1:] == 1))
        model += b[-1] == 0
    # lexicographic ordering of cols
    for c in range(N - 1):
        b = boolvar(N + 1)
        model += b[0] == 1
        model += b == ((matrix.T[c] <= matrix.T[c + 1]) &
                       ((matrix.T[c] < matrix.T[c + 1]) | b[1:] == 1))
        model += b[-1] == 0

    return model, matrix

def print_sol(matrix):
    print(matrix.value())
    print("Degree sequence:", end=" ")
    print(matrix.value().sum(axis=0))
    print()

if __name__ == "__main__":

    nb_iterations = 10

    tablesp_ortools =  PrettyTable(['Size of diamond', 'Number of Solutions', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'number of search branches', 'Overall Memory Usage (Bytes)'])
    tablesp_ortools.title = 'Results of the Diamond Free problem without CSE'
    tablesp_ortools_CSE =  PrettyTable(['Size of diamond', 'Number of Solutions', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'number of search branches', 'Overall Memory Usage (Bytes)'])
    tablesp_ortools_CSE.title = 'Results of the Diamond Free problem with CSE'    
    tablesp_ortools_factor =  PrettyTable(['Size of diamond', 'Number of Solutions', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'number of search branches', 'Overall Memory Usage (Bytes)'])
    tablesp_ortools_factor.title = 'Results of the Diamond Free problem'    

    for nb in range(10, 21):

        # Set a random seed for reproducibility reasons
        random.seed(0)

        parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("-n", type=int, default=nb, help="Size of diamond")
        parser.add_argument("--solution-limit", type=int, default=0, help="Number of solutions to find, find all by default")

        args = parser.parse_args()
        print(args.n)

        def run_code(slvr):
            start_model_time = timeit.default_timer()
            model, matrix = diamond_free(args.n)
            model_creation_time = timeit.default_timer() - start_model_time
            return model.solve(
                solver=slvr,
                time_limit=30), model_creation_time

        for slvr in ["ortools", "ortools_2"]:
            
            # Set random seed for same random conditions in both iterations
            random.seed(0)

            total_model_creation_time = []
            total_transform_time = []
            total_solve_time = []
            total_execution_time = []
            total_num_branches = []
            total_mem_usage = []

            for lp in range(nb_iterations):
                # Disable garbage collection for timing measurements
                gc.disable()

                initial_memory = psutil.Process().memory_info().rss
                start_time = timeit.default_timer()

                (n_sols, transform_time, solve_time, num_branches), model_creation_time = run_code(slvr)
                
                execution_time = timeit.default_timer() - start_time
                memory_usage = psutil.Process().memory_info().rss - initial_memory

                total_model_creation_time.append(model_creation_time)
                total_transform_time.append(transform_time)
                total_solve_time.append(solve_time)
                total_execution_time.append(execution_time)
                total_num_branches.append(num_branches)
                total_mem_usage.append(memory_usage)

                # Re-enable garbage collection
                gc.enable()

            if slvr == 'ortools':
                average_model_creation_time = sum(total_model_creation_time) / nb_iterations 
                average_transform_time = sum(total_transform_time) / nb_iterations
                average_solve_time = sum(total_solve_time) / nb_iterations 
                average_execution_time = sum(total_execution_time) / nb_iterations 
                average_num_branches = sum(total_num_branches) / nb_iterations 
                average_mem_usage = sum(total_mem_usage) / nb_iterations 

                tablesp_ortools.add_row([nb, n_sols, average_model_creation_time, average_transform_time, average_solve_time, average_execution_time, average_num_branches, average_mem_usage])
                with open("cpmpy/timing_results/diamond_free.txt", "w") as f:
                    f.write(str(tablesp_ortools))
                    f.write("\n")

            elif slvr == 'ortools_2':
                average_model_creation_time_2 = sum(total_model_creation_time) / nb_iterations
                average_transform_time_2 = sum(total_transform_time) / nb_iterations
                average_solve_time_2 = sum(total_solve_time) / nb_iterations
                average_execution_time_2 = sum(total_execution_time) / nb_iterations 
                average_num_branches_2 = sum(total_num_branches) / nb_iterations
                average_mem_usage_2 = sum(total_mem_usage) / nb_iterations

                tablesp_ortools_CSE.add_row([nb, n_sols, average_model_creation_time_2, average_transform_time_2, average_solve_time_2, average_execution_time_2, average_num_branches_2, average_mem_usage_2])
                with open("cpmpy/timing_results/diamond_free_CSE.txt", "w") as f:
                    f.write(str(tablesp_ortools_CSE))
                    f.write("\n")

                factor_model_creation_time = average_model_creation_time / average_model_creation_time_2
                factor_tranform_time = average_transform_time / average_transform_time_2
                factor_solve_time = average_solve_time / average_solve_time_2
                factor_execution_time = average_execution_time / average_execution_time_2
                factor_num_branches = average_num_branches / average_num_branches_2
                factor_mem_usage = average_mem_usage / average_mem_usage_2

                tablesp_ortools_factor.add_row([nb, n_sols, factor_model_creation_time, factor_tranform_time, factor_solve_time, factor_execution_time, factor_num_branches, factor_mem_usage])
                with open("cpmpy/CSE_results/diamond_free.txt", "w") as f:
                    f.write(str(tablesp_ortools_factor))
                    f.write("\n")