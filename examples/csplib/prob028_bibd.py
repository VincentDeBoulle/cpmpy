"""
Balanced Incomplete Block Design (BIBD) in cpmpy.

This is a port of Numberjack example Bibd.py:
'''
Balanced Incomplete Block Design (BIBD) --- CSPLib prob028

A BIBD is defined as an arrangement of v distinct objects into b blocks such
that each block contains exactly k distinct objects, each object occurs in
exactly r different blocks, and every two distinct objects occur together in
exactly lambda blocks. Another way of defining a BIBD is in terms of its
incidence matrix, which is a v by b binary matrix with exactly r ones per row,
k ones per column, and with a scalar product of lambda 'l' between any pair of
distinct rows.
'''

Model created by Hakan Kjellerstrand, hakank@hakank.com
See also my cpmpy page: http://www.hakank.org/cpmpy/

Modified by Ignace Bleukx, ignace.bleukx@kuleuven.be
"""
import gc
import sys
import timeit

from prettytable import PrettyTable
sys.path.append('../cpmpy')
import numpy as np

from cpmpy import *
from cpmpy.expressions.utils import all_pairs

def bibd(v, b, r, k, l):
    matrix = boolvar(shape=(v, b),name="matrix")

    model = Model()

    model += [sum(row) == r for row in matrix],    # every row adds up to r
    model += [sum(col) == k for col in matrix.T],  # every column adds up to k

    # the scalar product of every pair of columns adds up to l
    model += [np.dot(row_i, row_j) == l for row_i, row_j in all_pairs(matrix)]

    # break symmetry
    # lexicographic ordering of rows
    for r in range(v - 1):
        bvar = boolvar(shape=(b + 1))
        model += bvar[0] == 1
        model += bvar == ((matrix[r] <= matrix[r + 1]) &
                       ((matrix[r] < matrix[r + 1]) | bvar[1:] == 1))
        model += bvar[-1] == 0
    # lexicographic ordering of cols
    for c in range(b - 1):
        bvar = boolvar(shape=(v + 1))
        model += bvar[0] == 1
        model += bvar == ((matrix.T[c] <= matrix.T[c + 1]) &
                       ((matrix.T[c] < matrix.T[c + 1]) | bvar[1:] == 1))
        model += bvar[-1] == 0

    return model, (matrix,)


if __name__ == "__main__":
    import argparse

    nb_iterations = 100

    tablesp_ortools =  PrettyTable(['Values', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'number of search branches'])
    tablesp_ortools.title = f'Results of the Balanced Incomplete Block Design (BIBD) problem with CSE (average of {nb_iterations} iterations)'
    tablesp_ortools_noCSE =  PrettyTable(['Values', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'number of search branches'])
    tablesp_ortools_noCSE.title = f'Results of the Balanced Incomplete Block Design (BIBD) problem without CSE (average of {nb_iterations} iterations)'    

    for i in range(2, 11, 2):
        parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("--solution_limit", type=int, default=0, help="Number of solutions to find, find all by default")

        args = parser.parse_args()
        print("Number of i: ", i)

        default = {'v': 7*i, 'b': 7*i, 'r': 3*i, 'k': 3*i, 'l': 1*i}
        
        def create_model():
         return bibd(**default)

        model_creation_time = timeit.timeit(create_model, number = 1)    

        def run_code(slvr):
            start_model_time = timeit.default_timer()
            model, (matrix,) = bibd(**default)
            model_creation_time = timeit.default_timer() - start_model_time
            return model.solve(solver=slvr, time_limit=30), model_creation_time


        for slvr in ["ortools_noCSE", "ortools"]:
            total_model_creation_time = 0
            total_transform_time = 0
            total_solve_time = 0
            total_execution_time = 0
            total_num_branches = 0

            for lp in range(nb_iterations):
                # Disable garbage collection for timing measurements
                gc.disable()

                # Measure the model creation and execution time
                start_time = timeit.default_timer()
                (n_sols, transform_time, solve_time, num_branches), model_creation_time = run_code(slvr)
                execution_time = timeit.default_timer() - start_time

                total_model_creation_time += model_creation_time
                total_transform_time += transform_time
                total_solve_time += solve_time
                total_execution_time += execution_time
                total_num_branches += num_branches

                # Re-enable garbage collection
                gc.enable()
            
            average_model_creation_time = total_model_creation_time / nb_iterations
            average_transform_time = total_transform_time / nb_iterations
            average_solve_time = total_solve_time / nb_iterations
            average_execution_time = total_execution_time / nb_iterations
            average_num_branches = total_num_branches / nb_iterations

            if slvr == 'ortools':
                tablesp_ortools.add_row([default, average_model_creation_time, average_transform_time, average_solve_time, average_execution_time, average_num_branches])
                with open("cpmpy/timing_results/bibd_CSE.txt", "w") as f:
                    f.write(str(tablesp_ortools))
                    f.write("\n")
            else:
                tablesp_ortools_noCSE.add_row([default, average_model_creation_time, average_transform_time, average_solve_time, average_execution_time, num_branches])
                with open("cpmpy/timing_results/bibd.txt", "w") as f:
                    f.write(str(tablesp_ortools_noCSE))
                    f.write("\n")
