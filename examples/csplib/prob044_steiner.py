"""
Steiner triplets in CPMpy.

Problem 044 on CSPlib
csplib.org/Problems/prob044/

The ternary Steiner problem of order n consists of finding a set of n*(n−1)/6 triples of distinct integer elements in
{1,…,n} such that any two triples have at most one common element. It is a hypergraph problem coming from combinatorial
mathematics [luneburg1989tools] where n modulo 6 has to be equal to 1 or 3 [lindner2011topics].
One possible solution for n=7 is {{1, 2, 3}, {1, 4, 5}, {1, 6, 7}, {2, 4, 6}, {2, 5, 7}, {3, 4, 7}, {3, 5, 6}}.
The solution contains 7*(7−1)/6=7 triples.



Model created by Ignace Bleukx, ignace.bleukx@kuleuven.be
"""
import sys
import timeit
import numpy as np
from prettytable import PrettyTable
import gc

sys.path.append('../cpmpy')

from cpmpy import *
from cpmpy.expressions.utils import all_pairs

def steiner(n=15):
    assert n % 6 == 1 or n % 6 == 3, "N must be (1|3) modulo 6"

    n_sets = int(n * (n - 1) // 6)

    model = Model()

    # boolean representation of sets
    # sets[i,j] = true iff item j is part of set i
    sets = boolvar(shape=(n_sets, n), name="sets")

    # cardinality of set if 3
    # can be written cleaner, see issue #117
    # model += sum(sets, axis=0) == 3
    model += [sum(s) == 3 for s in sets]

    # cardinality of intersection <= 1
    for s1, s2 in all_pairs(sets):
        model += sum(s1 & s2) <= 1

    # symmetry breaking
    model += (sets[(0, 0)] == 1)

    return model, (sets,)

def print_sol(sets):
    for s in sets.value():
        print(np.where(s)[0], end=" ")
    print()


if __name__ == "__main__":
    import argparse

    tablesp_ortools =  PrettyTable(['Number of Sets', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Search Branches'])
    tablesp_ortools.title = 'Results of the Steiner problem with CSE (average of 10 iterations)'
    tablesp_ortools_noCSE =  PrettyTable(['Number of Sets', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Search Branches'])
    tablesp_ortools_noCSE.title = 'Results of the Steiner problem without CSE (average of 10 iterations)'    

    for num in range(3, 16, 3):
        parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("-num_sets", type=int, default=15, help="Number of sets")
        parser.add_argument("--solution_limit", type=int, default=0, help="Number of solutions to find, find all by default")

        args = parser.parse_args()

        print(num)

        def run_code(slvr):
            start_model_time = timeit.default_timer()
            model, (sets,) = steiner(args.num_sets)
            model_creation_time = timeit.default_timer() - start_model_time
            return model.solveAll(solver=slvr, solution_limit=args.solution_limit,
                                display=lambda : print_sol(sets)), model_creation_time

        for slvr in ["ortools_noCSE", "ortools"]:
            total_model_creation_time = 0
            total_transform_time = 0
            total_solve_time = 0
            total_execution_time = 0
            total_num_branches = 0

            for lp in range(10):
                # Disable garbage collection for timing measurements
                gc.disable()

                # Measure the model creation and execution time
                start_time = timeit.default_timer()
                (_, transform_time, solve_time, num_branches), model_creation_time = run_code(slvr)
                execution_time = timeit.default_timer() - start_time

                total_model_creation_time += model_creation_time
                total_transform_time += transform_time
                total_solve_time += solve_time
                total_execution_time += execution_time
                total_num_branches += num_branches

                # Re-enable garbage collection
                gc.enable()
        
        average_model_creation_time = total_model_creation_time / 10
        average_transform_time = total_transform_time / 10
        average_solve_time = total_solve_time / 10
        average_execution_time = total_execution_time / 10
        average_num_branches = total_num_branches /10

        if slvr == "ortools":
            tablesp_ortools.add_row([num, average_model_creation_time, average_transform_time, average_solve_time, average_execution_time, average_num_branches])
            with open("cpmpy/timing_results/steiner_CSE.txt", "w") as f:
                f.write(str(tablesp_ortools))
                f.write("\n")
        else:
            tablesp_ortools_noCSE.add_row([num, average_model_creation_time, average_transform_time, average_solve_time, average_execution_time, average_num_branches])
            with open("cpmpy/timing_results/steiner.txt", "w") as f:
                f.write(str(tablesp_ortools_noCSE))
                f.write("\n")
