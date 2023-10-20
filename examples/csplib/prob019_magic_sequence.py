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
    
    tablesp = PrettyTable(['Length of Sequence', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Branches'])

    for n in range(500, 600, 5):
        parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("-length", type=int, default=n, help="Length of the sequence, default is 10")

        args = parser.parse_args()

        def create_model():
            return magic_sequence(args.length)

        model_creation_time = timeit.timeit(create_model, number = 1)

        def run_code():
            model, (x,) = create_model()
            return model.solve()

        execution_time = timeit.timeit(run_code, number=1)
        _, transform_time, solve_time, num_branches = run_code()
        
        tablesp.add_row([args.length, model_creation_time, transform_time, solve_time, execution_time, num_branches])

        with open("cpmpy/timing_results/magic_sequence.txt", "w") as f:
            f.write(str(tablesp))
            f.write("\n")


