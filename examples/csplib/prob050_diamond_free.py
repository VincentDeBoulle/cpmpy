"""
Diamond-free Degree Sequences in cpmpy.

CSPLib Problem 050
http://www.csplib.org/Problems/prob050/

Fill in a binary matrix of size n * n in such a way that
- For every grouping of four rows, the sum of their non-symmetrical
  values is less than or equal to 4,
- No rows contain just zeroes,
- Every row has a sum modulo 3,
- The sum of the matrix is modulo 12.
- No row R contains a 1 in its Rth column.

Note on first constraint in model:
A group of four nodes can have at most four edges between them.
Since the matrix for this model will represent the adjacency
matrix of the graph, we need to take into consideration the fact
that the matrix will be symmetrical.

This is a port of the Numberjack example DiamondfreeDegreeSequences.py:

Model created by Hakan Kjellerstrand, hakank@hakank.com
See also my cpmpy page: http://www.hakank.org/cpmpy/

Modified by Ignace Bleukx, ignace.bleukx@kuleuven.be

"""
import sys
import numpy as np
import gc

sys.path.append('../cpmpy')

from cpmpy import *
from cpmpy.solvers import *
from itertools import combinations
import timeit
from prettytable import PrettyTable

def diamond_free(N=10):
    # By definition a and b will have the same cardinality:
    matrix = boolvar(shape=(N, N), name="matrix")

    model = Model()

    # No rows contain just zeroes.
    model += [sum(row) > 0 for row in matrix] # can be written cleaner, see issue #117
    # Every row has a sum modulo 3.
    model += [sum(row) % 3 == 0 for row in matrix]
    # The sum of the matrix is modulo 12.
    model += sum(matrix) % 12 == 0
    # No row R contains a 1 in its Rth column.
    model += [matrix[np.diag_indices(N)] == 0]

    # Every grouping of 4 rows can have at most a sum of 4 between them.
    for a, b, c, d in combinations(range(N), 4):
        model += sum([matrix[a][b], matrix[a][c], matrix[a][d],
                      matrix[b][c], matrix[b][d], matrix[c][d]]) <= 4

    # Undirected graph
    model += matrix == matrix.T

    # Symmetry breaking
    # lexicographic ordering of rows
    for r in range(N - 1):
        b = boolvar(N + 1)
        model += b[0] == 1
        model += b == ((matrix[r] <= matrix[r + 1]) &
                       ((matrix[r] < matrix[r + 1]) | b[1:] == 1))
        model += b[-1] == 0
    # lexicographic ordering of cols
    for c in range(N - 1):
        b = boolvar(N + 1)
        model += b[0] == 1
        model += b == ((matrix.T[c] <= matrix.T[c + 1]) &
                       ((matrix.T[c] < matrix.T[c + 1]) | b[1:] == 1))
        model += b[-1] == 0

    return model, matrix

def print_sol(matrix):
    print(matrix.value())
    print("Degree sequence:", end=" ")
    print(matrix.value().sum(axis=0))
    print()

if __name__ == "__main__":
    import argparse

    tablesp = PrettyTable(['Size of diamond', 'Number of Solutions', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'number of search branches'])

    for nb in range(10, 21):
        parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("-n", type=int, default=nb, help="Size of diamond")
        parser.add_argument("--solution-limit", type=int, default=0, help="Number of solutions to find, find all by default")

        args = parser.parse_args()
        print(args.n)

        def create_model():
            return diamond_free(args.n)
        
        model_creation_time = timeit.timeit(create_model, number = 1)

        def run_code():
            model, matrix = create_model()
            return model.solveAll(
                solution_limit=args.solution_limit,
                time_limit=30)

        # Disable garbage collection for timing measurements
        gc.disable()

        # Measure the model creation and execution time
        start_time = timeit.default_timer()
        n_sols, transform_time, solve_time, num_branches = run_code()
        execution_time = timeit.default_timer() - start_time

        # Re-enable garbage collection
        gc.enable()

        tablesp.add_row([nb, n_sols, model_creation_time, transform_time, solve_time, execution_time, num_branches])

        with open("cpmpy/timing_results/diamond_free.txt", "w") as f:
            f.write(str(tablesp))
            f.write("\n")

