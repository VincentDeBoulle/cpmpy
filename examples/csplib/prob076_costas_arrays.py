"""
Costas array in cpmpy.
https://www.csplib.org/Problems/prob076/

From http://mathworld.wolfram.com/CostasArray.html:

An order-n Costas array is a permutation on {1,...,n} such
that the distances in each row of the triangular difference
table are distinct. For example, the permutation {1,3,4,2,5}
has triangular difference table {2,1,-2,3}, {3,-1,1}, {1,2},
and {4}. Since each row contains no duplications, the permutation
is therefore a Costas array.


This cpmpy model was written by Hakan Kjellerstrand (hakank@gmail.com)
See also my cpmpy page: http://hakank.org/cpmpy/

Modified by Ignace Bleukx, ignace.bleukx@kuleuven.be
"""
import timeit
import numpy as np
import sys
import gc

from prettytable import PrettyTable

sys.path.append('../cpmpy')

from cpmpy import *

def costas_array(n=6):
    print(f"n: {n}")
    model = Model()

    # declare variables
    costas = intvar(1, n, shape=n, name="costas")
    differences = intvar(-n + 1, n - 1, shape=(n, n), name="differences")

    tril_idx = np.tril_indices(n, -1)
    triu_idx = np.triu_indices(n, 1)

    # constraints

    # Fix the values in the lower triangle in the
    # difference matrix to -n+1. This removes variants
    # of the difference matrix for the the same Costas array.
    model += differences[tril_idx] == -n + 1

    # hakank: All the following constraints are from
    # Barry O'Sullivans's original model.
    model += [AllDifferent(costas)]

    # "How do the positions in the Costas array relate
    #  to the elements of the distance triangle."
    for i,j in zip(*triu_idx):
        model += [differences[(i, j)] == costas[j] - costas[j - i - 1]]

    # "All entries in a particular row of the difference
    #  triangle must be distinct."
    for i in range(n - 2):
        model += [AllDifferent([differences[i, j] for j in range(n) if j > i])]

    #
    # "All the following are redundant - only here to speed up search."
    #

    # "We can never place a 'token' in the same row as any other."
    model += differences[triu_idx] != 0

    for k,l in zip(*triu_idx):
        if k < 2 or l < 2:
            continue
        model += [differences[k - 2, l - 1] + differences[k, l] ==
                  differences[k - 1, l - 1] + differences[k - 1, l]]

    return model, (costas, differences)


def print_sol(costas, differences):
    n = len(costas)
    print("costas:", costas.value())
    print("differences:")
    for i, row in enumerate(differences.value()[:-1]):
        print(row[i+1:])


if __name__ == "__main__":
    import argparse

    nb_iterations = 10

    tablesp_ortools =  PrettyTable(['Size', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Search Branches'])
    tablesp_ortools.title = 'Results of the Costas Arrays problem without CSE'
    tablesp_ortools_CSE =  PrettyTable(['Size', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Search Branches'])
    tablesp_ortools_CSE.title = 'Results of the Costas Arrays problem with CSE'    
    tablesp_ortools_factor =  PrettyTable(['Size', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Search Branches'])
    tablesp_ortools_factor.title = 'Results of the Costas Arrays problem'

    for sz in range(5, 15):
        parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("-size", type=int, default=sz, help="Size of array")
        parser.add_argument("--solution_limit", type=int, default=0, help="Number of solutions, find all by default")

        args = parser.parse_args()
        print(args.size)

        def run_code(slvr):
            start_model_time = timeit.default_timer()
            model, (costas, differences) = costas_array(args.size)
            model_creation_time = timeit.default_timer() - start_model_time
            return model.solve(solver=slvr), model_creation_time

        for slvr in ["ortools", "ortools_CSE"]:
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
                (_, transform_time, solve_time, num_branches), model_creation_time = run_code(slvr)
                execution_time = timeit.default_timer() - start_time

                total_model_creation_time.append(model_creation_time)
                total_transform_time.append(transform_time)
                total_solve_time.append(solve_time)
                total_execution_time.append(execution_time)
                total_num_branches.append(num_branches)

                # Re-enable garbage collection
                gc.enable()

            if slvr == 'ortools':
                average_model_creation_time = sum(total_model_creation_time) / nb_iterations
                average_transform_time = sum(total_transform_time) / nb_iterations
                average_solve_time = sum(total_solve_time) / nb_iterations
                average_execution_time = sum(total_execution_time) / nb_iterations
                average_num_branches = sum(total_num_branches) / nb_iterations

                tablesp_ortools.add_row([args.size, average_model_creation_time, average_transform_time, average_solve_time, average_execution_time, average_num_branches])
                with open("cpmpy/timing_results/costas_arrays.txt", "w") as f:
                    f.write(str(tablesp_ortools))
                    f.write("\n")
            if slvr == 'ortools':
                average_model_creation_time_2 = sum(total_model_creation_time) / nb_iterations 
                average_transform_time_2 = sum(total_transform_time) / nb_iterations
                average_solve_time_2 = sum(total_solve_time) / nb_iterations
                average_execution_time_2 = sum(total_execution_time) / nb_iterations
                average_num_branches_2 = sum(total_num_branches) / nb_iterations

                tablesp_ortools_CSE.add_row([args.size, average_model_creation_time_2, average_transform_time_2, average_solve_time_2, average_execution_time_2, average_num_branches_2])
                with open("cpmpy/timing_results/costas_arrays_CSE.txt", "w") as f:
                    f.write(str(tablesp_ortools_CSE))
                    f.write("\n")

                factor_model_creation_time = average_model_creation_time / average_model_creation_time_2
                factor_tranform_time = average_transform_time / average_transform_time_2
                factor_solve_time = average_solve_time / average_solve_time_2
                factor_execution_time = average_execution_time / average_execution_time_2
                factor_num_branches = average_num_branches / average_num_branches_2

                tablesp_ortools_factor.add_row([args.size, factor_model_creation_time, factor_tranform_time, factor_solve_time, factor_execution_time, factor_num_branches])
                with open("cpmpy/CSE_results/costas_arrays.txt", "w") as f:
                    f.write(str(tablesp_ortools_factor))
                    f.write("\n")