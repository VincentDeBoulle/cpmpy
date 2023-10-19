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

from prettytable import PrettyTable
sys.path.append('../cpmpy')

from cpmpy import *
import json
import timeit

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
    import argparse
    import json
    import requests

    # Get all problem names out of the JSON (future proof if json changes)
    with open('examples/csplib/prob001_car_sequence.json', 'r') as json_file:
        data = json.load(json_file)
    
    problem_names = [problem['name'] for problem in data]

    tablesp = PrettyTable(['Problem Name', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Branches'])
    
    for name in problem_names:
        # argument parsing
        url = "https://raw.githubusercontent.com/CPMpy/cpmpy/master/examples/csplib/prob001_car_sequence.json"
        parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
        #parser.add_argument('-instance', nargs='?', default="Problem 4/72  (Regin & Puget #1)", help="Name of the problem instance found in file 'filename'")
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
            return car_sequence(**problem_params)
        
        model_creation_time = timeit.timeit(create_model, number = 1)

        def run_code():
            model, (slots, setup) = car_sequence(**problem_params)
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

        with open("cpmpy/timing_results/car_sequence.txt", "w") as f:
            f.write(str(tablesp))
            f.write("\n")