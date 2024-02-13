"""
Car sequencing in CPMpy (prob001 in CSPlib)
A number of cars are to be produced; they are not identical, because different options are available as variants on the basic model.
The assembly line has different stations which install the various options (air-conditioning, sun-roof, etc.).
These stations have been designed to handle at most a certain percentage of the cars passing along the assembly line.
Furthermore, the cars requiring a certain option must not be bunched together, otherwise the station will not be able to cope.
Consequently, the cars must be arranged in a sequence so that the capacity of each station is never exceeded.
For instance, if a particular station can only cope with at most half of the cars passing along the line, the sequence must be built so that at most 1 car in any 2 requires that option.
The problem has been shown to be NP-complete (Gent 1999).

https://www.csplib.org/Problems/prob001/

Based on the Minizinc model car.mzn.

Data format compatible with both variations of model (with and without block constraints)
Model was created by Ignace Bleukx, ignace.bleukx@kuleuven.be
"""
import sys
sys.path.append('../cpmpy')

from cpmpy import *
from prettytable import PrettyTable
import json
import timeit
import gc
import argparse
import requests

def car_sequence(n_cars, n_options, n_classes, n_cars_p_class, options, capacity=None, blocks=None, **kwargs):
    # build model
    model = Model()

    # decision variables
    slots = intvar(0, n_classes - 1, shape=n_cars, name="slots")
    setup = boolvar(shape=(n_cars, n_options), name="setup")

    # convert options to cpm_array
    options = cpm_array(options)

    # satisfy demand
    model += [sum(slots == c) == n_cars_p_class[c] for c in range(n_classes)]

    # car has correct options
    # This can be written cleaner, see issue #117 on github
    # m += [setup[s] == options[slots[s]] for s in range(n_cars)]
    for s in range(n_cars):
        model += [setup[s, o] == options[slots[s], o] for o in range(n_options)]

    if capacity is not None and blocks is not None:
        # satisfy block capacity
        for o in range(n_options):
            setup_seq = setup[:, o]
            # get all setups within block size of each other
            windows = zip(*[setup_seq[b:] for b in range(blocks[o])])
            for block in windows:
                model += sum(block) <= capacity[o]

    return model, (slots, setup)


# Helper functions
def _get_instance(data, pname):
    for entry in data:
        if pname == entry["name"]:
            return entry
    raise ValueError(f"Problem instance with name '{pname}' not found, use --list-instances to get the full list.")


def _print_instances(data):
    import pandas as pd
    df = pd.json_normalize(data)
    df_str = df.to_string(columns=["name", "n_cars", "n_options", "n_classes", "note"], na_rep='-')
    print(df_str)


if __name__ == "__main__":

    nb_iterations = 10

    # Get all problem names out of the JSON (future proof if json changes)
    with open('examples/csplib/prob001_car_sequence.json', 'r') as json_file:
        data = json.load(json_file)

    problem_names = [problem['name'] for problem in data]

    tablesp_ortools =  PrettyTable(['Problem Name', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Branches'])
    tablesp_ortools.title = 'Results of the Car Sequence problem without CSE'
    tablesp_ortools_CSE =  PrettyTable(['Problem Name', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Branches'])
    tablesp_ortools_CSE.title = 'Results of the Car Sequence problem without CSE'
    tablesp_ortools_factor =  PrettyTable(['Problem Name', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Branches'])
    tablesp_ortools_factor.title = 'Results of the Car Sequence problem'

    for name in problem_names:
        # argument parsing
        url = "https://raw.githubusercontent.com/CPMpy/cpmpy/master/examples/csplib/prob001_car_sequence.json"
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
            model, (_, _) = car_sequence(**problem_params)
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
                return 404, 404, 404, 404
        
        total_model_creation_time = []
        total_model_creation_time_CSE = []
        total_transform_time = []
        total_transform_time_CSE = []
        total_solve_time = []
        total_execution_time = []
        total_num_branches = []
        for slvr in ["ortools", "ortools_CSE"]:

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
                with open("cpmpy/timing_results/car_sequence.txt", "w") as f:
                    f.write(str(tablesp_ortools))
                    f.write("\n")

            elif slvr == 'ortools_CSE':
                average_model_creation_time_2 = sum(total_model_creation_time) / nb_iterations 
                average_transform_time_2 = sum(total_transform_time) / nb_iterations
                average_solve_time_2 = sum(total_solve_time) / nb_iterations
                average_execution_time_2 = sum(total_execution_time) / nb_iterations
                average_num_branches_2 = sum(total_num_branches) / nb_iterations

                tablesp_ortools_CSE.add_row([name, average_model_creation_time_2, average_transform_time_2, average_solve_time_2, average_execution_time_2, average_num_branches_2])
                with open("cpmpy/timing_results/car_sequence_CSE.txt", "w") as f:
                    f.write(str(tablesp_ortools_CSE))
                    f.write("\n")

                factor_model_creation_time = average_model_creation_time / average_model_creation_time_2
                factor_tranform_time = average_transform_time / average_transform_time_2
                factor_solve_time = average_solve_time / average_solve_time_2
                factor_execution_time = average_execution_time / average_execution_time_2
                factor_num_branches = average_num_branches / average_num_branches_2

                tablesp_ortools_factor.add_row([name, factor_model_creation_time, factor_tranform_time, factor_solve_time, factor_execution_time, factor_num_branches])
                with open("cpmpy/CSE_results/car_sequence.txt", "w") as f:
                    f.write(str(tablesp_ortools_factor))
                    f.write("\n")
