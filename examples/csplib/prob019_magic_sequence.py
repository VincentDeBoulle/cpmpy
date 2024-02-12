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
import timeit
import numpy as np
from prettytable import PrettyTable
import gc

sys.path.append('../cpmpy')

from cpmpy import *
import argparse


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
    
    tablesp_ortools =  PrettyTable(['Length of Sequence', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Branches'])
    tablesp_ortools.title = f'Results of the Magic Sequence problem with CSE (average of ${nb_iterations}$ iterations)'
    tablesp_ortools_noCSE =  PrettyTable(['Length of Sequence', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Branches'])
    tablesp_ortools_noCSE.title = f'Results of the Magic Sequence problem without CSE (average of ${nb_iterations}$ iterations)'    

    for n in range(100, 155, 5):
        parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("-length", type=int, default=n, help="Length of the sequence, default is 10")

        args = parser.parse_args()

        def run_code(slvr):
            start_model_time = timeit.default_timer()
            model, (x,) = magic_sequence(args.length)
            model_creation_time = timeit.default_timer() - start_model_time

            return model.solve(solver=slvr), model_creation_time

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

            average_model_creation_time = sum(total_model_creation_time) / nb_iterations
            average_transform_time = sum(total_transform_time) / nb_iterations
            average_solve_time = sum(total_solve_time) / nb_iterations
            average_execution_time = sum(total_execution_time) / nb_iterations
            average_num_branches = sum(total_num_branches) / nb_iterations
        
            if slvr == 'ortools':
                tablesp_ortools.add_row([args.length, average_model_creation_time, average_transform_time, average_solve_time, average_execution_time, average_num_branches])
                with open("cpmpy/timing_results/magic_sequence.txt", "w") as f:
                    f.write(str(tablesp_ortools))
                    f.write("\n")
