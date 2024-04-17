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
import numpy as np
import sys
import gc
import psutil
import random
import timeit
import argparse

sys.path.append('../cpmpy')

from cpmpy import *
from prettytable import PrettyTable

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

    nb_iterations = 10

    tablesp_ortools =  PrettyTable(['Amount of numbers to partition', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Overall Memory Usage (Bytes)'])
    tablesp_ortools.title = 'Results of the Number Partitioning problem without CSE'
    tablesp_ortools_CSE =  PrettyTable(['Amount of numbers to partition', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Overall Memory Usage (Bytes)'])
    tablesp_ortools_CSE.title = 'Results of the Number Partitioning problem with CSE'    
    tablesp_ortools_factor =  PrettyTable(['Amount of numbers to partition', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Overall Memory Usage (Bytes)'])
    tablesp_ortools_factor.title = 'Results of the Number Partitioning problem'    

    for nb in range(10,23,2):

        # Set a random seed for reproducibility reasons
        random.seed(0)

        parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("-n", type=int, default=nb, help="Amount of numbers to partition")

        n = parser.parse_args().n
        print(n)  

        def run_code(slvr):
            start_model_time = timeit.default_timer()
            model, (x,y) = number_partitioning(n)
            model_creation_time = timeit.default_timer() - start_model_time
            return model.solve(solver=slvr, time_limit=30), model_creation_time

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

                tablesp_ortools.add_row([nb, average_model_creation_time, average_transform_time, average_solve_time, average_execution_time, average_mem_usage])
                with open("cpmpy/timing_results/number_partitioning_z3.txt", "w") as f:
                    f.write(str(tablesp_ortools))
                    f.write("\n")

            elif slvr == 'z3_2':
                average_model_creation_time_2 = sum(total_model_creation_time) / nb_iterations
                average_transform_time_2 = sum(total_transform_time) / nb_iterations
                average_solve_time_2 = sum(total_solve_time) / nb_iterations
                average_execution_time_2 = sum(total_execution_time) / nb_iterations 
                average_mem_usage_2 = sum(total_mem_usage) / nb_iterations

                tablesp_ortools_CSE.add_row([nb, average_model_creation_time_2, average_transform_time_2, average_solve_time_2, average_execution_time_2, average_mem_usage_2])
                with open("cpmpy/timing_results/number_partitioning_z3_CSE.txt", "w") as f:
                    f.write(str(tablesp_ortools_CSE))
                    f.write("\n")

                factor_model_creation_time = average_model_creation_time / average_model_creation_time_2
                factor_tranform_time = average_transform_time / average_transform_time_2
                factor_solve_time = average_solve_time / average_solve_time_2
                factor_execution_time = average_execution_time / average_execution_time_2
                factor_mem_usage = average_mem_usage / average_mem_usage_2

                tablesp_ortools_factor.add_row([nb, factor_model_creation_time, factor_tranform_time, factor_solve_time, factor_execution_time, factor_mem_usage])
                with open("cpmpy/CSE_results/number_partitioning_z3.txt", "w") as f:
                    f.write(str(tablesp_ortools_factor))
                    f.write("\n")