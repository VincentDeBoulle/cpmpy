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
sys.path.append('../cpmpy')

import timeit
from prettytable import PrettyTable
from cpmpy import *
import gc

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
    import argparse

    tablesp_ortools = PrettyTable(['Size', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Search Branches'])
    tablesp_ortools.title = 'OR-Tools: Results of the Golomb problem with CSE (average of 50 iterations)'
    tablesp_ortools_noCSE = PrettyTable(['Size', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Search Branches'])
    tablesp_ortools_noCSE.title = 'OR-Tools: Results of the Golomb problem without CSE (average of 50 iterations)'
    tablesp_exact_noCSE = PrettyTable(['Size', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Search Branches'])
    tablesp_exact_noCSE.title = 'Exact: Results of the Golomb problem without CSE (average of 20 iterations)'

    for sz in range(8, 20):

        parser = argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("-size", type=int, default=sz, help="Size of the ruler")

        size = parser.parse_args().size
        print(size)

        def run_code(slvr):
            start_model_time = timeit.default_timer()
            model, (marks, ) = golomb(size)
            model_creation_time = timeit.default_timer() - start_model_time
            return model.solve(solver=slvr), model_creation_time

        for slvr in ['ortools_noCSE', 'ortools']:
            total_model_creation_time = 0
            total_transform_time = 0
            total_solve_time = 0
            total_execution_time = 0
            total_num_branches = 0

            for lp in range(50):
                # Disable garbage collection for timing measurements
                #gc.disable()

                # Measure the model creation and execution time
                start_time = timeit.default_timer()
                (n_sols, transform_time, solve_time, num_branches), model_creation_time = run_code(slvr)
                execution_time = timeit.default_timer() - start_time
                
                total_model_creation_time += model_creation_time
                total_transform_time += transform_time
                total_solve_time += solve_time
                total_execution_time += execution_time
                total_num_branches += num_branches
            
                # Re-enable garbage collection
                #gc.enable()

            average_model_creation_time = total_model_creation_time / 50
            average_transform_time = total_transform_time / 50
            average_solve_time = total_solve_time / 50
            average_execution_time = total_execution_time / 50
            average_num_branches = total_num_branches / 50

            if slvr == 'ortools':
                tablesp_ortools.add_row([size, average_model_creation_time, average_transform_time, average_solve_time, average_execution_time, average_num_branches])
                with open("cpmpy/timing_results/2_golomb_CSE.txt", "w") as f:
                    f.write(str(tablesp_ortools))
                    f.write("\n")
            elif slvr == 'ortools_noCSE':
                tablesp_ortools_noCSE.add_row([size, average_model_creation_time, average_transform_time, average_solve_time, average_execution_time, num_branches])
                with open("cpmpy/timing_results/2_golomb.txt", "w") as f:
                    f.write(str(tablesp_ortools_noCSE))
                    f.write("\n")
            else:
                tablesp_exact_noCSE.add_row([size, average_model_creation_time, average_transform_time, average_solve_time, average_execution_time, num_branches])
                with open("cpmpy/timing_results/2_golomb.txt", "w") as f:
                    f.write(str(tablesp_ortools_noCSE))
                    f.write("\n")

