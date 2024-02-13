"""
    Vessel loading in CPMpy
    Problem 008 in CSPlib

    Model inspired by Essence implementation on CSPlib

    Created by Ignace Bleukx

"""

import sys
import requests
import json
import gc
import numpy as np

sys.path.append('../cpmpy')

from cpmpy import *
from cpmpy.expressions.utils import all_pairs
import timeit
from prettytable import PrettyTable

def vessel_loading(deck_width, deck_length, n_containers, width, length, classes, separation, **kwargs):

    # setup data
    containers = list(range(n_containers))
    classes = np.array(classes)
    separation = np.array(separation)

    model = Model()

    # layout of containers
    left = intvar(0, deck_width, shape=n_containers, name="left")
    right = intvar(0, deck_width, shape=n_containers, name="right")
    top = intvar(0, deck_length, shape=n_containers, name="top")
    bottom = intvar(0, deck_length, shape=n_containers, name="bottom")

    # set shape of containers
    model += (
            (((right - left) == width) & ((top - bottom) == length)) # along shipdeck
                                        |
            (((right - left) == length) & ((top - bottom) == width)) # accross shipdeck
    )


    # no overlap between containers
    for x,y in all_pairs(containers):
        c1,c2 = classes[[x,y]]
        sep = separation[c1-1,c2-1]
        model += (
                (right[x] + sep <= left[y]) | # x at least sep left of y or
                (left[x] >= right[y] + sep) | # x at least sep right of y or
                (top[x] + sep <= bottom[y]) | # x at least sep under y or
                (bottom[x] >= top[y] + sep)   # x at least sep above y
        )

    return model, (left, right, top, bottom)

def _get_instance(data, pname):
    for entry in data:
        if pname == entry["name"]:
            return entry
    raise ValueError(f"Problem instance with name {pname} not found, use --list-instances to get the full list.")


def _print_instances(data):
    import pandas as pd
    df = pd.json_normalize(data)
    df_str = df.to_string(columns=["name", "deck_width", "deck_length", "n_containers", "n_classes"], na_rep='-')
    print(df_str)


if __name__ == "__main__":
    import argparse
    import json
    import requests

    nb_iterations = 10

    # Get all problem names out of the JSON (future proof if json changes)
    with open('examples/csplib/prob008_vessel_loading.json', 'r') as json_file:
        data = json.load(json_file)
    
    problem_names = [problem['name'] for problem in data]

    tablesp_ortools =  PrettyTable(['Problem Name', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Branches'])
    tablesp_ortools.title = 'Results of the Car Sequence problem without CSE'
    tablesp_ortools_CSE =  PrettyTable(['Problem Name', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Branches'])
    tablesp_ortools_CSE.title = 'Results of the Car Sequence problem with CSE'
    tablesp_ortools_factor =  PrettyTable(['Problem Name', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Branches'])
    tablesp_ortools_factor.title = 'Results of the Car Sequence problem'

    for name in problem_names:
        # argument parsing
        url = "https://raw.githubusercontent.com/CPMpy/cpmpy/csplib/examples/csplib/prob008_vessel_loading.json"
        parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument('-instance', default=name, help="Name of the problem instance found in file 'filename'")
        parser.add_argument('-filename', default=url, help="File containing problem instances, can be local file or url")
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
        
        print("Problem name: ", problem_params["name"])
        
        def run_code(slvr):
            start_model_time = timeit.default_timer()
            model, (left, right, top, bottom) = vessel_loading(**problem_params)
            model_creation_time = timeit.default_timer() - start_model_time
            ret, transform_time, solve_time, num_branches = model.solve(solver=slvr, time_limit=20)

            # solve the model
            if ret:
                print("Solved this problem")
                return model_creation_time, transform_time, solve_time, num_branches
                
            elif model.status().runtime > 19:
                print("This problem passes the time limit")
                return 408, 408, 408, 408
            else:
                print("Model is unsatisfiable!")
                return 404, 404, 404, 404
            
        for slvr in ["ortools", "ortools_CSE"]:
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
                model_creation_time,transform_time, solve_time, num_branches = run_code(slvr)
                execution_time = timeit.default_timer() - start_time

                total_model_creation_time.append(model_creation_time)
                total_transform_time.append(transform_time)
                total_solve_time.append(solve_time)
                total_execution_time.append(execution_time)
                total_num_branches.append(num_branches)

                # Re-enable garbage collection
                gc.enable()

            if slvr == 'ortools':
                average_model_creation_time = sum(total_model_creation_time) / nb_iterations
                average_transform_time = sum(total_transform_time) / nb_iterations
                average_solve_time = sum(total_solve_time) / nb_iterations
                average_execution_time = sum(total_execution_time) / nb_iterations
                average_num_branches = sum(total_num_branches) / nb_iterations

                tablesp_ortools.add_row([name, average_model_creation_time, average_transform_time, average_solve_time, average_execution_time, average_num_branches])
                with open("cpmpy/timing_results/vessel_loading.txt", "w") as f:
                    f.write(str(tablesp_ortools))
                    f.write("\n")

            elif slvr == 'ortools_CSE':
                average_model_creation_time_2 = sum(total_model_creation_time) / nb_iterations 
                average_transform_time_2 = sum(total_transform_time) / nb_iterations
                average_solve_time_2 = sum(total_solve_time) / nb_iterations
                average_execution_time_2 = sum(total_execution_time) / nb_iterations
                average_num_branches_2 = sum(total_num_branches) / nb_iterations

                tablesp_ortools_CSE.add_row([name, average_model_creation_time_2, average_transform_time_2, average_solve_time_2, average_execution_time_2, average_num_branches_2])
                with open("cpmpy/timing_results/vessel_loading_CSE.txt", "w") as f:
                    f.write(str(tablesp_ortools_CSE))
                    f.write("\n")

                factor_model_creation_time = average_model_creation_time / average_model_creation_time_2
                factor_tranform_time = average_transform_time / average_transform_time_2
                factor_solve_time = average_solve_time / average_solve_time_2
                factor_execution_time = average_execution_time / average_execution_time_2
                factor_num_branches = average_num_branches / average_num_branches_2

                tablesp_ortools_factor.add_row([name, factor_model_creation_time, factor_tranform_time, factor_solve_time, factor_execution_time, factor_num_branches])
                with open("cpmpy/CSE_results/vessel_loading.txt", "w") as f:
                    f.write(str(tablesp_ortools_factor))
                    f.write("\n")

