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

    tablesp = PrettyTable(['Amount of numbers to partition', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'number of search branches'])

    for nb in range(10,101,10):
        parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("-n", type=int, default=nb, help="Amount of numbers to partition")

        n = parser.parse_args().n
        print(n)
        
        def create_model():
            return number_partitioning(n)

        model_creation_time = timeit.timeit(create_model, number = 1)    

        def run_code():
            model, (x,y) = create_model()
            return model.solve(time_limit=30)

        # Measure the execution time
        execution_time = timeit.timeit(run_code, number=1)

        n_sols, transform_time, solve_time, num_branches = run_code()
        tablesp.add_row([nb, model_creation_time, transform_time, solve_time, execution_time, num_branches])

        with open("cpmpy/timing_results/number_partitioning.txt", "w") as f:
            f.write(str(tablesp))
            f.write("\n")