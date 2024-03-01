"""
Magic sequence in cpmpy.

Problem 019 on CSPlib
https://www.csplib.org/Problems/prob019/

A magic sequence of length n is a sequence of integers x0 . . xn-1 between
0 and n-1, such that for all i in 0 to n-1, the number i occurs exactly xi
times in the sequence. For instance, 6,2,1,0,0,0,1,0,0,0 is a magic sequence
since 0 occurs 6 times in it, 1 occurs twice, ...

Model created by Hakan Kjellerstrand, hakank@hakank.com
See also my cpmpy page: http://www.hakank.org/cpmpy/

Modified by Ignace Bleukx, ignace.bleukx@kuleuven.be
"""
import sys
import gc
import random
import timeit
import psutil
import argparse


sys.path.append('../cpmpy')

import numpy as np
from prettytable import PrettyTable
from cpmpy import *

def magic_sequence(n):
    print("n:", n)
    model = Model()

    x = intvar(0, n - 1, shape=n, name="x")

    # constraints
    for i in range(n):
        model += x[i] == sum(x == i)

    # speedup search
    model += sum(x) == n
    model += sum(x * np.arange(n)) == n

    return model, (x,)

if __name__ == "__main__":

    nb_iterations = 10

    tablesp_ortools =  PrettyTable(['Values', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'number of search branches', 'Overall Memory Usage (Bytes)'])
    tablesp_ortools.title = 'Results of the Magic Sequence problem without CSE'
    tablesp_ortools_CSE =  PrettyTable(['Values', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'number of search branches', 'Overall Memory Usage (Bytes)'])
    tablesp_ortools_CSE.title = 'Results of the Magic Sequence problem problem with CSE'    
    tablesp_ortools_factor =  PrettyTable(['Values', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'number of search branches', 'Overall Memory Usage (Bytes)'])
    tablesp_ortools_factor.title = 'Results of the Magic Sequence problem problem'    

    for i in range(10, 20):

        # Set a random seed for reproducibility reasons
        random.seed(0)
    
        parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("-length", type=int, default=i, help="Length of the sequence, default is 10")

        args = parser.parse_args()
        print("Number of i: ", i )

        def run_code(slvr):
            start_model_time = timeit.default_timer()
            model, (x,) = magic_sequence(args.length)
            model_creation_time = timeit.default_timer() - start_model_time
            return model.solve(solver=slvr), model_creation_time
        
        for slvr in ["ortools", "ortools_CSE"]:
            
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

                tablesp_ortools.add_row([i, average_model_creation_time, average_transform_time, average_solve_time, average_execution_time, average_num_branches, average_mem_usage])
                with open("cpmpy/timing_results/magic_sequence.txt", "w") as f:
                    f.write(str(tablesp_ortools))
                    f.write("\n")
            elif slvr == 'ortools_CSE':
                average_model_creation_time_2 = sum(total_model_creation_time) / nb_iterations
                average_transform_time_2 = sum(total_transform_time) / nb_iterations
                average_solve_time_2 = sum(total_solve_time) / nb_iterations
                average_execution_time_2 = sum(total_execution_time) / nb_iterations 
                average_num_branches_2 = sum(total_num_branches) / nb_iterations
                average_mem_usage_2 = sum(total_mem_usage) / nb_iterations

                tablesp_ortools_CSE.add_row([i, average_model_creation_time_2, average_transform_time_2, average_solve_time_2, average_execution_time_2, average_num_branches_2, average_mem_usage_2])
                with open("cpmpy/timing_results/magic_sequence_CSE.txt", "w") as f:
                    f.write(str(tablesp_ortools_CSE))
                    f.write("\n")

                factor_model_creation_time = average_model_creation_time / average_model_creation_time_2
                factor_tranform_time = average_transform_time / average_transform_time_2
                factor_solve_time = average_solve_time / average_solve_time_2
                factor_execution_time = average_execution_time / average_execution_time_2
                factor_num_branches = average_num_branches / average_num_branches_2
                factor_mem_usage = average_mem_usage / average_mem_usage_2

                tablesp_ortools_factor.add_row([i, factor_model_creation_time, factor_tranform_time, factor_solve_time, factor_execution_time, factor_num_branches, factor_mem_usage])
                with open("cpmpy/CSE_results/magic_sequence.txt", "w") as f:
                    f.write(str(tablesp_ortools_factor))
                    f.write("\n")