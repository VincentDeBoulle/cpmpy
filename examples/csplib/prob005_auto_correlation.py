"""
    Minimizing autocorrelation of bitarray in CPMpy

    Problem 005 on CSPlib

    Model created by Ignace Bleukx, ignace.bleukx@kuleuven.be
"""
import argparse
import sys

sys.path.append('../cpmpy')

import numpy as np

from cpmpy import *
import timeit
from prettytable import PrettyTable
import gc

def auto_correlation(n=16):

    # bitarray of length n
    arr = intvar(-1,1,shape=n, name="arr")

    model = Model()

    # exclude 0
    model += arr != 0

    # minimize sum of squares
    model.minimize(
        sum([PAF(arr,s) ** 2 for s in range(1,n)])
    )

    return model, (arr,)

# periodic auto correlation
def PAF(arr, s):
    # roll the array 's' indices
    return sum(arr * np.roll(arr,-s))


if __name__ == "__main__":

    nb_iterations = 10

    tablesp_ortools = PrettyTable(['Length', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Search Branches'])
    tablesp_ortools.title = 'Results of the Auto Correlation problem without CSE'
    tablesp_ortools_CSE = PrettyTable(['Length', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Search Branches'])
    tablesp_ortools_CSE.title = 'Results of the Auto Correlation problem with CSE'
    tablesp_ortools_factor = PrettyTable(['Length', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Search Branches'])
    tablesp_ortools_factor.title = 'Results of the Auto Correlation problem'

    for lngth in range(10, 25):
        parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("-length", nargs='?', type=int, default=lngth, help="Length of bitarray")

        length = parser.parse_args().length
        print(length)

        def create_model():
            return auto_correlation(length)
        
        model_creation_time = timeit.timeit(create_model, number=1)

        def run_code(slvr):
            start_model_time = timeit.default_timer()
            model, (arr,) = auto_correlation(length)
            model_creation_time = timeit.default_timer() - start_model_time
            return model.solve(solver=slvr, time_limit=30), model_creation_time

        for slvr in ['ortools', 'ortools_CSE']:
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
                average_model_creation_time = sum(sorted(total_model_creation_time)[:3]) / 3 
                average_transform_time = sum(sorted(total_transform_time)[:3]) / 3 
                average_solve_time = sum(sorted(total_solve_time)[:3]) / 3 
                average_execution_time = sum(sorted(total_execution_time)[:3]) / 3 
                average_num_branches = sum(sorted(total_num_branches)[:3]) / 3 

                tablesp_ortools.add_row([length, average_model_creation_time, average_transform_time, average_solve_time, average_execution_time, average_num_branches])
                with open("cpmpy/timing_results/auto_correlation.txt", "w") as f:
                    f.write(str(tablesp_ortools))
                    f.write("\n")

            elif slvr == 'ortools_CSE':
                average_model_creation_time_2 = sum(sorted(total_model_creation_time)[:3]) / 3 
                average_transform_time_2 = sum(sorted(total_transform_time)[:3]) / 3 
                average_solve_time_2 = sum(sorted(total_solve_time)[:3]) / 3 
                average_execution_time_2 = sum(sorted(total_execution_time)[:3]) / 3 
                average_num_branches_2 = sum(sorted(total_num_branches)[:3]) / 3 

                tablesp_ortools_CSE.add_row([length, average_model_creation_time_2, average_transform_time_2, average_solve_time_2, average_execution_time_2, average_num_branches_2])
                with open("cpmpy/timing_results/auto_correlation_CSE.txt", "w") as f:
                    f.write(str(tablesp_ortools_CSE))
                    f.write("\n")

                factor_model_creation_time = average_model_creation_time / average_model_creation_time_2
                factor_tranform_time = average_transform_time / average_transform_time_2
                factor_solve_time = average_solve_time / average_solve_time_2
                factor_execution_time = average_execution_time / average_execution_time_2
                factor_num_branches = average_num_branches / average_num_branches_2

                tablesp_ortools_factor.add_row([length, factor_model_creation_time, factor_tranform_time, factor_solve_time, factor_execution_time, factor_num_branches])
                with open("cpmpy/CSE_results/auto_correlation.txt", "w") as f:
                    f.write(str(tablesp_ortools_factor))
                    f.write("\n")