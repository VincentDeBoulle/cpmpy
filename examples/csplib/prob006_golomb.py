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

    tablesp = PrettyTable(['Size', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Search Branches'])

    for sz in range(5, 16):

        parser = argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("-size", type=int, default=sz, help="Size of the ruler")

        size = parser.parse_args().size
        print(size)

        def create_model():
            return golomb(size)
        
        model_creation_time = timeit.timeit(create_model, number=1)

        def run_code():
            model, (marks, ) = create_model()
            return model.solve()

        # Disable garbage collection for timing measurements
        gc.disable()

        # Measure the model creation and execution time
        start_time = timeit.default_timer()
        n_sols, transform_time, solve_time, num_branches = run_code()
        execution_time = timeit.default_timer() - start_time

        # Re-enable garbage collection
        gc.enable()

        tablesp.add_row([size, model_creation_time, transform_time, solve_time, execution_time, num_branches])

        with open("cpmpy/timing_results/golomb.txt", "w") as f:
            f.write(str(tablesp))
            f.write("\n")

