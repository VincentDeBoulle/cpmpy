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
import sys
import numpy as np
from prettytable import PrettyTable
sys.path.append('../cpmpy')

from cpmpy import *
from cpmpy.expressions.utils import all_pairs
import json
import timeit


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

    import argparse
    import json
    import requests

    # Get all problem names out of the JSON (future proof if json changes)
    with open('examples/csplib/prob009_perfect_squares.json', 'r') as json_file:
        data = json.load(json_file)
    
    problem_names = [problem['name'] for problem in data]

    tablesp = PrettyTable(['Problem Name', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Branches'])
    
    for name in problem_names:
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

        def create_model():
            return perfect_squares(**problem_params)
        
        model_creation_time = timeit.timeit(create_model, number=1)

        def run_code():
            model, (x_coords, y_coords) = create_model()
            ret, transform_time, solve_time, num_branches = model.solve(time_limit=20)
            if ret:
                print("Solved this problem")
                return transform_time, solve_time, num_branches
                
            elif model.status().runtime > 19:
                print("This problem passes the time limit")
                return 'Passes limit', 'Passes limit', 'Passes limit'
            else:
                print("Model is unsatisfiable!")
                return 'Unsatisfiable', 'Unsatisfiable', 'Unsatisfiable'

        
        execution_time = timeit.timeit(run_code, number=1)
        transform_time, solve_time, num_branches = run_code()
        
        tablesp.add_row([name, model_creation_time, transform_time, solve_time, execution_time, num_branches])

        with open("cpmpy/timing_results/perfect_squares.txt", "w") as f:
            f.write(str(tablesp))
            f.write("\n")
