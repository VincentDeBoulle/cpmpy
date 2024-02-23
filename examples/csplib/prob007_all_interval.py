"""
All interval problem in cpmpy.

CSPLib problem number 007
https://www.csplib.org/Problems/prob007/


Given the twelve standard pitch-classes (c, c#, d, …), represented by numbers 0,1,…,11, find a series in which each
pitch-class occurs exactly once and in which the musical intervals between neighbouring notes cover the full set of
intervals from the minor second (1 semitone) to the major seventh (11 semitones). That is, for each of the intervals,
there is a pair of neighbouring pitch-classes in the series, between which this interval appears.

The problem of finding such a series can be easily formulated as an instance of a more general arithmetic problem on
ℤn, the set of integer residues modulo n. Given n∈ℕ, find a vector s=(s1,…,sn), such that

s is a permutation of {0,1,…,n−1}; and the interval vector v=(|s2−s1|,|s3−s2|,…|sn−sn−1|) is a permutation of {1,2,…,
n−1}. A vector v satisfying these conditions is called an all-interval series of size n; the problem of finding such
a series is the all-interval series problem of size n. We may also be interested in finding all possible series of a
given size.

Model created by Hakan Kjellerstrand, hakank@hakank.com
See also my cpmpy page: http://www.hakank.org/cpmpy/

Modified by Ignace Bleukx, ignace.bleukx@kuleuven.be
"""
import argparse
import sys

sys.path.append('../cpmpy')

from cpmpy import *
import numpy as np
import timeit
import gc
from prettytable import PrettyTable
import random

def all_interval(n=12):

    # Create the solver.
    model = Model()

    # declare variables
    x = intvar(1,n,shape=n,name="x")
    diffs = intvar(1,n-1,shape=n-1,name="diffs")

    # constraints
    model += [AllDifferent(x),
              AllDifferent(diffs)]

    # differences between successive values
    model += diffs == np.abs(x[1:] - x[:-1])

    # symmetry breaking
    model += [x[0] < x[-1]] # mirroring array is equivalent solution
    model += [diffs[0] < diffs[1]] #

    return model, (x, diffs)

def print_solution(x, diffs):
    print(f"x:    {x.value()}")
    print(f"diffs: {diffs.value()}")
    print()

if __name__ == "__main__":

    nb_iterations = 10

    tablesp_ortools = PrettyTable(['length', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Search Branches'])
    tablesp_ortools.title = 'Results of the All Interval problem without CSE'
    tablesp_ortools_CSE = PrettyTable(['length', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Search Branches'])
    tablesp_ortools_CSE.title = 'Results of the All Interval problem with CSE'
    tablesp_ortools_factor = PrettyTable(['length', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Search Branches'])
    tablesp_ortools_factor.title = 'Results of the All Interval problem'

    for lngth in range(15, 30):
        random.seed(0)
        
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("-length", type=int,help="Length of array, 12 by default", default=lngth)
        parser.add_argument("--solution_limit", type=int, help="Number of solutions to find, find all by default", default=0)

        print(lngth)
        args = parser.parse_args()
        
        def run_code(slvr):
            start_model_time = timeit.default_timer()
            model, (x, diffs) = all_interval(args.length)
            model_creation_time = timeit.default_timer() - start_model_time
            return model.solve(solver=slvr), model_creation_time

        for slvr in ["ortools", "ortools_2"]:
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

            if slvr == 'ortools':
                average_model_creation_time = sum(total_model_creation_time) / nb_iterations 
                average_transform_time = sum(total_transform_time) / nb_iterations
                average_solve_time = sum(total_solve_time) / nb_iterations 
                average_execution_time = sum(total_execution_time) / nb_iterations 
                average_num_branches = sum(total_num_branches) / nb_iterations 

                tablesp_ortools.add_row([lngth, average_model_creation_time, average_transform_time, average_solve_time, average_execution_time, average_num_branches])
                with open("cpmpy/timing_results/all_interval.txt", "w") as f:
                    f.write(str(tablesp_ortools))
                    f.write("\n")

            elif slvr == 'ortools_2':
                average_model_creation_time_2 = sum(total_model_creation_time) / nb_iterations
                average_transform_time_2 = sum(total_transform_time) / nb_iterations
                average_solve_time_2 = sum(total_solve_time) / nb_iterations
                average_execution_time_2 = sum(total_execution_time) / nb_iterations 
                average_num_branches_2 = sum(total_num_branches) / nb_iterations

                tablesp_ortools_CSE.add_row([lngth, average_model_creation_time_2, average_transform_time_2, average_solve_time_2, average_execution_time_2, average_num_branches_2])
                with open("cpmpy/timing_results/all_interval_CSE.txt", "w") as f:
                    f.write(str(tablesp_ortools_CSE))
                    f.write("\n")

                factor_model_creation_time = average_model_creation_time / average_model_creation_time_2
                factor_tranform_time = average_transform_time / average_transform_time_2
                factor_solve_time = average_solve_time / average_solve_time_2
                factor_execution_time = average_execution_time / average_execution_time_2
                factor_num_branches = average_num_branches / average_num_branches_2

                tablesp_ortools_factor.add_row([lngth, factor_model_creation_time, factor_tranform_time, factor_solve_time, factor_execution_time, factor_num_branches])
                with open("cpmpy/CSE_results/all_interval.txt", "w") as f:
                    f.write(str(tablesp_ortools_factor))
                    f.write("\n")