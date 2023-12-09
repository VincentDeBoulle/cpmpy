"""
Problem 049 on CSPLib
https://www.csplib.org/Problems/prob049/

This problem consists in finding a partition of numbers 1..N into two sets A and B such that:

A and B have the same cardinality
sum of numbers in A = sum of numbers in B
sum of squares of numbers in A = sum of squares of numbers in B
There is no solution for N<8.

Adapted from pycsp3 implementation: https://raw.githubusercontent.com/xcsp3team/pycsp3/master/problems/csp/academic/NumberPartitioning.py

Modified by Ignace Bleukx, ignace.bleukx@kuleuven.be
"""
import sys
import numpy as np
import gc

sys.path.append('../cpmpy')

import timeit
from prettytable import PrettyTable
from cpmpy import *

def number_partitioning(n=8):
    assert n % 2 == 0, "The value of n must be even"

    # x[i] is the ith value of the first set
    x = intvar(1, n, shape=n // 2)

    # y[i] is the ith value of the second set
    y = intvar(1, n, shape=n // 2)

    model = Model()

    model += AllDifferent(np.append(x, y))

    # sum of numbers is equal in both sets
    model += sum(x) == sum(y)

    # sum of squares is equal in both sets
    model += sum(x ** 2) == sum(y ** 2)

    # break symmetry
    model += x[:-1] <= x[1:]
    model += y[:-1] <= x[1:]

    return model, (x,y)

if __name__ == "__main__":
    import argparse

    nb_iterations = 10

    tablesp_ortools =  PrettyTable(['Amount of numbers to partition', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'number of search branches'])
    tablesp_ortools.title = f'Results of the Number Partitioning problem with CSE (average of {nb_iterations} iterations)'
    tablesp_ortools_noCSE =  PrettyTable(['Amount of numbers to partition', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'number of search branches'])
    tablesp_ortools_noCSE.title = f'Results of the Number Partitioning problem without CSE (average of {nb_iterations} iterations)'    

    for nb in range(20,201,10):
        parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("-n", type=int, default=nb, help="Amount of numbers to partition")

        n = parser.parse_args().n
        print(n)
        
        def create_model():
            return number_partitioning(n)

        model_creation_time = timeit.timeit(create_model, number = 1)    

        def run_code(slvr):
            start_model_time = timeit.default_timer()
            model, (x,y) = number_partitioning(n)
            model_creation_time = timeit.default_timer() - start_model_time
            return model.solve(solver=slvr, time_limit=30), model_creation_time

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
                tablesp_ortools.add_row([nb, average_model_creation_time, average_transform_time, average_solve_time, average_execution_time, average_num_branches])
                with open("cpmpy/timing_results/number_partitioning_CSE.txt", "w") as f:
                    f.write(str(tablesp_ortools))
                    f.write("\n")
