"""
Hadamard matrix Legendre pairs in CPMpy.
Problem 084 on CSPlib

Model created by Ignace Bleukx, ignace.bleukx@kuleuven.be
"""
import random
import sys
import gc
import psutil
import argparse
import numpy as np
import timeit

sys.path.append('../cpmpy')

from cpmpy import *
from prettytable import PrettyTable

def PAF(arr, s):
    return sum(arr * np.roll(arr,-s))

def hadmard_matrix(l=5):

    m = int((l - 1) / 2)

    a = intvar(-1,1, shape=l, name="a")
    b = intvar(-1,1, shape=l, name="b")

    model = Model()

    model += a != 0 # exclude 0 from dom
    model += b != 0 # exclude 0 from dom

    model += sum(a) == 1
    model += sum(b) == 1

    for s in range(1,m+1):
        model += (PAF(a,s) + PAF(b,s)) == -2

    return model, (a,b)

if __name__ == "__main__":

    nb_iterations = 10

    tablesp_ortools =  PrettyTable(['Length of Sequence', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Overall Memory Usage (Bytes)'])
    tablesp_ortools.title = 'Results of the Hadamard matrix problem without CSE'
    tablesp_ortools_CSE =  PrettyTable(['Length of Sequence', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Overall Memory Usage (Bytes)'])
    tablesp_ortools_CSE.title = 'Results of the Hadamard matrix problem with CSE'   
    tablesp_ortools_factor =  PrettyTable(['Length of Sequence', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Overall Memory Usage (Bytes)'])
    tablesp_ortools_factor.title = 'Results of the Hadamard matrix problem' 

    for lngth in range(15, 26, 2):

        # Set a random seed for reproducibility reasons
        random.seed(0)

        parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("-length", type=int, default=lngth, help="Length of sequence")

        l = parser.parse_args().length
        print(l)

        def run_code(slvr):
            start_model_time = timeit.default_timer()
            model, (a,b) = hadmard_matrix(l)
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

                tablesp_ortools.add_row([l, average_model_creation_time, average_transform_time, average_solve_time, average_execution_time, average_mem_usage])
                with open("cpmpy/timing_results/hadamard_matrix_z3.txt", "w") as f:
                    f.write(str(tablesp_ortools))
                    f.write("\n")

            if slvr == 'z3_2':
                average_model_creation_time_2 = sum(total_model_creation_time) / nb_iterations
                average_transform_time_2 = sum(total_transform_time) / nb_iterations
                average_solve_time_2 = sum(total_solve_time) / nb_iterations
                average_execution_time_2 = sum(total_execution_time) / nb_iterations 
                average_mem_usage_2 = sum(total_mem_usage) / nb_iterations

                tablesp_ortools_CSE.add_row([l, average_model_creation_time_2, average_transform_time_2, average_solve_time_2, average_execution_time_2, average_mem_usage_2])
                with open("cpmpy/timing_results/hadamard_matrix_z3_CSE.txt", "w") as f:
                    f.write(str(tablesp_ortools_CSE))
                    f.write("\n")

                factor_model_creation_time = average_model_creation_time / average_model_creation_time_2
                factor_tranform_time = average_transform_time / average_transform_time_2
                factor_solve_time = average_solve_time / average_solve_time_2
                factor_execution_time = average_execution_time / average_execution_time_2
                factor_mem_usage = average_mem_usage / average_mem_usage_2

                tablesp_ortools_factor.add_row([l, factor_model_creation_time, factor_tranform_time, factor_solve_time, factor_execution_time, factor_mem_usage])
                with open("cpmpy/CSE_results/hadamard_matrix_z3.txt", "w") as f:
                    f.write(str(tablesp_ortools_factor))
                    f.write("\n")