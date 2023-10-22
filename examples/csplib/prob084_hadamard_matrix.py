"""
Hadamard matrix Legendre pairs in CPMpy.
Problem 084 on CSPlib

Model created by Ignace Bleukx, ignace.bleukx@kuleuven.be
"""
import sys
import gc
sys.path.append('../cpmpy')

# load the libraries
import numpy as np
from cpmpy import *
import timeit
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
    import argparse

    tablesp = PrettyTable(['Length of Sequence', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'number of search branches'])


    for lngth in range(15, 35, 2):
        parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("-length", type=int, default=lngth, help="Length of sequence")

        l = parser.parse_args().length
        print(l)

        def create_model():
            return hadmard_matrix(l)
        
        model_creation_time = timeit.timeit(create_model, number=1)

        def run_code():
            model, (a,b) = create_model()
            return model.solve(time_limit=30)

        # Disable garbage collection for timing measurements
        gc.disable()

        # Measure the model creation and execution time
        start_time = timeit.default_timer()
        n_sols, transform_time, solve_time, num_branches = run_code()
        execution_time = timeit.default_timer() - start_time

        # Re-enable garbage collection
        gc.enable()

        tablesp.add_row([l, model_creation_time, transform_time, solve_time, execution_time, num_branches])

        with open("cpmpy/timing_results/hadamard_matrix.txt", "w") as f:
            f.write(str(tablesp))
            f.write("\n")