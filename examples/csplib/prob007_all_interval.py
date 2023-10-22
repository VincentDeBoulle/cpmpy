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
import sys
import argparse
import timeit
import gc
from prettytable import PrettyTable

sys.path.append('../cpmpy')

from cpmpy import *
import numpy as np


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

    tablesp = PrettyTable(['length', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Search Branches'])

    for lngth in range(5, 16):
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument("-length", type=int,help="Length of array, 12 by default", default=lngth)
        parser.add_argument("--solution_limit", type=int, help="Number of solutions to find, find all by default", default=0)

        print(lngth)
        args = parser.parse_args()

        def create_model():
            return all_interval(args.length)
        
        model_creation_time = timeit.timeit(create_model, number=1)
        
        def run_code():
            model, (x, diffs) = create_model()
            return model.solveAll(solution_limit=args.solution_limit,
                                display=lambda: print_solution(x, diffs))
        
        # Disable garbage collection for timing measurements
        gc.disable()

        # Measure the model creation and execution time
        start_time = timeit.default_timer()
        n_sols, transform_time, solve_time, num_branches = run_code()
        execution_time = timeit.default_timer() - start_time

        # Re-enable garbage collection
        gc.enable()

        tablesp.add_row([lngth, model_creation_time, transform_time, solve_time, execution_time, num_branches])

        with open("cpmpy/timing_results/all_interval.txt", "w") as f:
            f.write(str(tablesp))
            f.write("\n")