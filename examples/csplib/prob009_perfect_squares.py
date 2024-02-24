"""
Perfect squares problem in cpmpy.

CSPLib prob 009: Perfect square placements
http://www.cs.st-andrews.ac.uk/~ianm/CSPLib/prob/prob009/index.html
'''
The perfect square placement problem (also called the squared square
problem) is to pack a set of squares with given integer sizes into a
bigger square in such a way that no squares overlap each other and all
square borders are parallel to the border of the big square. For a
perfect placement problem, all squares have different sizes. The sum of
the square surfaces is equal to the surface of the packing square, so
that there is no spare capacity. A simple perfect square placement
problem is a perfect square placement problem in which no subset of
the squares (greater than one) are placed in a rectangle.
'''
Inspired by implementation of Vessel Packing problem (008)
Model created by Ignace Bleukx, ignace.bleukx@kuleuven.be
"""
import random
import sys
import numpy as np
import json
import timeit
import gc
import psutil
import argparse
import json
import requests

sys.path.append('../cpmpy')

from cpmpy import *
from prettytable import PrettyTable
from cpmpy.expressions.utils import all_pairs

def perfect_squares(base, sides, **kwargs):
    model = Model()
    sides = np.array(sides)

    squares = range(len(sides))

    # Ensure that the squares cover the base exactly
    assert np.square(sides).sum() == base ** 2, "Squares do not cover the base exactly!"

    # variables
    x_coords = intvar(0, base, shape=len(squares), name="x_coords")
    y_coords = intvar(0, base, shape=len(squares), name="y_coords")

    # squares must be in bounds of big square
    model += x_coords + sides <= base
    model += y_coords + sides <= base

    # no overlap between coordinates
    for a, b in all_pairs(squares):
        model += (
            (x_coords[a] + sides[a] <= x_coords[b]) |
            (x_coords[b] + sides[b] <= x_coords[a]) |
            (y_coords[a] + sides[a] <= y_coords[b]) |
            (y_coords[b] + sides[b] <= y_coords[a])
        )

    return model, (x_coords, y_coords)

def _get_instance(data, pname):
    for entry in data:
        if pname == entry["name"]:
            return entry
    raise ValueError(f"Problem instance with name '{pname}' not found, use --list-instances to get the full list.")


def _print_instances(data):
    import pandas as pd
    df = pd.json_normalize(data)
    df_str = df.to_string(columns=["name", "base", "sides", "note"], na_rep='-')
    print(df_str)


if __name__ == "__main__":

    nb_iterations = 10

    # Get all problem names out of the JSON (future proof if json changes)
    with open('examples/csplib/prob009_perfect_squares.json', 'r') as json_file:
        data = json.load(json_file)
    
    problem_names = [problem['name'] for problem in data]

    tablesp_ortools =  PrettyTable(['Problem Name', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Branches', 'Overall Memory Usage (Bytes)'])
    tablesp_ortools.title = 'Results of the Perfect Squares problem without CSE'
    tablesp_ortools_CSE =  PrettyTable(['Problem Name', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Branches', 'Overall Memory Usage (Bytes)'])
    tablesp_ortools_CSE.title = 'Results of the Perfect Squares problem with CSE'    
    tablesp_ortools_factor =  PrettyTable(['Problem Name', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Branches', 'Overall Memory Usage (Bytes)'])
    tablesp_ortools_factor.title = 'Results of the Perfect Squares problem'  

    for name in problem_names:

        # Set a random seed for reproducibility reasons
        random.seed(0)

        # argument parsing
        url = "https://raw.githubusercontent.com/CPMpy/cpmpy/csplib/examples/csplib/prob009_perfect_squares.json"
        parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument('-instance', nargs='?', default=name, help="Name of the problem instance found in file 'filename'")
        parser.add_argument('-filename', nargs='?', default=url, help="File containing problem instances, can be local file or url")
        parser.add_argument('--list-instances', help='List all problem instances', action='store_true')

        args = parser.parse_args()

        if "http" in args.filename:
            problem_data = requests.get(args.filename).json()
        else:
            with open(args.filename, "r") as f:
                problem_data = json.load(f)

        if args.list_instances:
            _print_instances(problem_data)
            exit(0)

        problem_params = _get_instance(problem_data, args.instance)
        print("Problem name:", problem_params["name"])

        def run_code(slvr):
            start_model_time = timeit.default_timer()
            model, (x_coords, y_coords) = perfect_squares(**problem_params)
            model_creation_time = timeit.default_timer() - start_model_time
            
            ret, transform_time, solve_time, num_branches = model.solve(solver=slvr, time_limit=20)
            if ret:
                print("Solved this problem")
                return model_creation_time, transform_time, solve_time, num_branches
                
            elif model.status().runtime > 19:
                print("This problem passes the time limit")
                return 408, 408, 408, 408
            else:
                print("Model is unsatisfiable!")
                return 400, 400, 400, 400

        for slvr in ["ortools", "ortools_2"]:
            
            # Set random seed for same random conditions in both iterations
            random.seed(0)

            total_model_creation_time = []
            total_transform_time = []
            total_solve_time = []
            total_execution_time = []
            total_num_branches = []
            total_mem_usage = []

            for lp in range(nb_iterations):
                # Disable garbage collection for timing measurements
                gc.disable()

                initial_memory = psutil.Process().memory_info().rss
                start_time = timeit.default_timer()

                model_creation_time, transform_time, solve_time, num_branches = run_code(slvr)
                
                execution_time = timeit.default_timer() - start_time
                memory_usage = psutil.Process().memory_info().rss - initial_memory

                total_model_creation_time.append(model_creation_time)
                total_transform_time.append(transform_time)
                total_solve_time.append(solve_time)
                total_execution_time.append(execution_time)
                total_num_branches.append(num_branches)
                total_mem_usage.append(memory_usage)

                # Re-enable garbage collection
                gc.enable()

            if slvr == 'ortools':
                average_model_creation_time = sum(total_model_creation_time) / nb_iterations 
                average_transform_time = sum(total_transform_time) / nb_iterations
                average_solve_time = sum(total_solve_time) / nb_iterations 
                average_execution_time = sum(total_execution_time) / nb_iterations 
                average_num_branches = sum(total_num_branches) / nb_iterations 
                average_mem_usage = sum(total_mem_usage) / nb_iterations

                tablesp_ortools.add_row([name, average_model_creation_time, average_transform_time, average_solve_time, average_execution_time, average_num_branches, average_mem_usage])
                with open("cpmpy/timing_results/perfect_squares.txt", "w") as f:
                    f.write(str(tablesp_ortools))
                    f.write("\n")

            elif slvr == 'ortools_2':
                average_model_creation_time_2 = sum(total_model_creation_time) / nb_iterations
                average_transform_time_2 = sum(total_transform_time) / nb_iterations
                average_solve_time_2 = sum(total_solve_time) / nb_iterations
                average_execution_time_2 = sum(total_execution_time) / nb_iterations 
                average_num_branches_2 = sum(total_num_branches) / nb_iterations
                average_mem_usage_2 = sum(total_mem_usage) / nb_iterations

                tablesp_ortools_CSE.add_row([name, average_model_creation_time_2, average_transform_time_2, average_solve_time_2, average_execution_time_2, average_num_branches_2, average_mem_usage_2])
                with open("cpmpy/timing_results/perfect_squares_CSE.txt", "w") as f:
                    f.write(str(tablesp_ortools_CSE))
                    f.write("\n")

                factor_model_creation_time = average_model_creation_time / average_model_creation_time_2
                factor_tranform_time = average_transform_time / average_transform_time_2
                factor_solve_time = average_solve_time / average_solve_time_2
                factor_execution_time = average_execution_time / average_execution_time_2
                factor_num_branches = average_num_branches / average_num_branches_2
                factor_mem_usage = average_mem_usage / average_mem_usage_2

                tablesp_ortools_factor.add_row([name, factor_model_creation_time, factor_tranform_time, factor_solve_time, factor_execution_time, factor_num_branches, factor_mem_usage])
                with open("cpmpy/CSE_results/perfect_squares.txt", "w") as f:
                    f.write(str(tablesp_ortools_factor))
                    f.write("\n")