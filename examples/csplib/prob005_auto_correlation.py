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

    tablsp = PrettyTable(['Length', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Search Branches'])


    for lngth in range(10, 25):
        parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("-length", nargs='?', type=int, default=lngth, help="Length of bitarray")

        length = parser.parse_args().length
        print(length)

        def create_model():
            return auto_correlation(length)
        
        model_creation_time = timeit.timeit(create_model, number=1)

        def run_code():
            model, (arr,) = create_model()
            return model.solve(time_limit=30)
        
        execution_time = timeit.timeit(run_code, number=1)

        _, transform_time, solve_time, num_branches = run_code()
        tablsp.add_row([length, model_creation_time, transform_time, solve_time, execution_time, num_branches])

        with open("cpmpy/timing_results/auto_correlation.txt", "w") as f:
            f.write(str(tablsp))
            f.write("\n")