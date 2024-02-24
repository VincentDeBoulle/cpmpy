"""
Golomb's ruler problem in cpmpy.

Problem 006 on CSPlib
https://www.csplib.org/Problems/prob006/

A Golomb ruler is a set of integers (marks) a(1) < ...  < a(n) such
that all the differences a(i)-a(j) (i > j) are distinct.  Clearly we
may assume a(1)=0.  Then a(n) is the length of the Golomb ruler.
For a given number of marks, n, we are interested in finding the
shortest Golomb rulers.  Such rulers are called optimal.

Also, see:
- https://en.wikipedia.org/wiki/Golomb_ruler
- http://www.research.ibm.com/people/s/shearer/grule.html


Model created by Hakan Kjellerstrand, hakank@hakank.com
See also my cpmpy page: http://www.hakank.org/cpmpy/

Modified by Ignace Bleukx, ignace.bleukx@kuleuven.be
"""
import sys
import random
import psutil
import gc
import timeit
import argparse

sys.path.append('../cpmpy')

from prettytable import PrettyTable
from cpmpy import *

def golomb(size=10):

    marks = intvar(0, size*size, shape=size, name="marks")

    model = Model()
    # first mark is 0
    model += (marks[0] == 0)
    # marks must be increasing
    model += marks[:-1] < marks[1:]

    # golomb constraint
    diffs = [marks[j] - marks[i] for i in range(0, size-1)
                                 for j in range(i+1, size)]
    model += AllDifferent(diffs)

    # Symmetry breaking
    model += (marks[size - 1] - marks[size - 2] > marks[1] - marks[0])
    model += (diffs[0] < diffs[size - 1])

    # find optimal ruler
    model.minimize(marks[-1])

    return model, (marks,)

if __name__ == "__main__":

    nb_iterations = 10

    tablesp_ortools = PrettyTable(['Size', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Search Branches', 'Overall Memory Usage (Bytes)'])
    tablesp_ortools.title = 'OR-Tools: Results of the Golomb problem without CSE'
    tablesp_ortools_CSE = PrettyTable(['Size', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Search Branches', 'Overall Memory Usage (Bytes)'])
    tablesp_ortools_CSE.title = 'OR-Tools: Results of the Golomb problem with CSE'
    tablesp_ortools_factor = PrettyTable(['Size', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Search Branches', 'Overall Memory Usage (Bytes)'])
    tablesp_ortools_factor.title = 'OR-Tools: Results of the Golomb problem'

    for sz in range(10, 26):

        # Set a random seed for reproducibility reasons
        random.seed(0)

        parser = argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("-size", type=int, default=sz, help="Size of the ruler")

        size = parser.parse_args().size
        print(size)

        def run_code(slvr):

            start_model_time = timeit.default_timer()

            model, (marks, ) = golomb(size)

            model_creation_time = timeit.default_timer() - start_model_time

            return model.solve(solver=slvr), model_creation_time

        for slvr in ['ortools', 'ortools_2']:

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

                tablesp_ortools.add_row([size, average_model_creation_time, average_transform_time, average_solve_time, average_execution_time, average_num_branches, average_mem_usage])
                with open("cpmpy/timing_results/golomb.txt", "w") as f:
                    f.write(str(tablesp_ortools))
                    f.write("\n")

            elif slvr == 'ortools_2':
                average_model_creation_time_2 = sum(total_model_creation_time) / nb_iterations
                average_transform_time_2 = sum(total_transform_time) / nb_iterations
                average_solve_time_2 = sum(total_solve_time) / nb_iterations
                average_execution_time_2 = sum(total_execution_time) / nb_iterations 
                average_num_branches_2 = sum(total_num_branches) / nb_iterations
                average_mem_usage_2 = sum(total_mem_usage) / nb_iterations 

                tablesp_ortools_CSE.add_row([size, average_model_creation_time_2, average_transform_time_2, average_solve_time_2, average_execution_time_2, average_num_branches_2, average_mem_usage_2])
                with open("cpmpy/timing_results/golomb_CSE.txt", "w") as f:
                    f.write(str(tablesp_ortools_CSE))
                    f.write("\n")

                factor_model_creation_time = average_model_creation_time / average_model_creation_time_2
                factor_tranform_time = average_transform_time / average_transform_time_2
                factor_solve_time = average_solve_time / average_solve_time_2
                factor_execution_time = average_execution_time / average_execution_time_2
                factor_num_branches = average_num_branches / average_num_branches_2
                factor_mem_usage = average_mem_usage / average_mem_usage_2

                tablesp_ortools_factor.add_row([size, factor_model_creation_time, factor_tranform_time, factor_solve_time, factor_execution_time, factor_num_branches, factor_mem_usage])
                with open("cpmpy/CSE_results/golomb.txt", "w") as f:
                    f.write(str(tablesp_ortools_factor))
                    f.write("\n")