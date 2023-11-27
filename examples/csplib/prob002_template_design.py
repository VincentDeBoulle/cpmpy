"""
Template design in CPMpy (prob002 in CSPlib)
https://www.csplib.org/Problems/prob002/

This problem arises from a colour printing firm which produces a variety of products from thin board,
including cartons for human and animal food and magazine inserts. Food products, for example, are often marketed as a
basic brand with several variations (typically flavours). Packaging for such variations usually has the same overall
design, in particular the same size and shape, but differs in a small proportion of the text displayed and/or in
colour. For instance, two variations of a cat food carton may differ only in that on one is printed ‘Chicken Flavour’
on a blue background whereas the other has ‘Rabbit Flavour’ printed on a green background. A typical order is for a
variety of quantities of several design variations. Because each variation is identical in dimension, we know in
advance exactly how many items can be printed on each mother sheet of board, whose dimensions are largely determined
by the dimensions of the printing machinery. Each mother sheet is printed from a template, consisting of a thin
aluminium sheet on which the design for several of the variations is etched. The problem is to decide, firstly,
how many distinct templates to produce, and secondly, which variations, and how many copies of each, to include on
each template. The following example is based on data from an order for cartons for different varieties of dry
cat-food.

Implementation based on Minizinc model in CSPlib.
Model created by Ignace Bleukx, ignace.bleukx@kuleuven.be
"""
import sys
import timeit
import json
from prettytable import PrettyTable
import requests
import argparse
import numpy as np
import gc

sys.path.append('../cpmpy')

from cpmpy import *

def template_design(n_slots, n_templates, n_var, demand,**kwargs):

    ub = max(demand)

    # create model
    model = Model()

    # decision variables
    production = intvar(1, ub, shape=n_templates, name="production")
    layout = intvar(0,n_var, shape=(n_templates,n_var), name="layout")

    # all slots are populated in a template
    model += all(sum(layout[i]) == n_slots for i in range(n_templates))

    # meet demand
    for var in range(n_var):
        model += sum(production * layout[:,var]) >= demand[var]

    # break symmetry
    # equal demand
    for i in range(n_var-1):
        if demand[i] == demand[i+1]:
            model += layout[0,i] <= layout[0,i+1]
            for j in range(n_templates-1):
                model += (layout[j,i] == layout[j,i+1]).implies \
                         (layout[j+1,i] <= layout[j+1,i+1])

    # distinguish templates
    for i in range(n_templates-1):
        model += production[i] <= production[i+1]

    # static symmetry
    for i in range(n_var-1):
        if demand[i] < demand[i+1]:
            model += sum(production * layout[:,i]) <= sum(production * layout[:,i+1])

    # minimize number of printed sheets
    model.minimize(sum(production))

    return model, (production, layout)


def _get_instance(data, pname):
    for entry in data:
        if pname == entry["name"]:
            return entry
    raise ValueError(f"Problem instance with name {pname} not found, use --list-instances to get the full list.")

def _print_instances(data):
    import pandas as pd
    df = pd.json_normalize(data)
    df_str = df.to_string(columns=["name", "n_slots", "n_templates", "n_var"], na_rep='-')
    print(df_str)

if __name__ == "__main__":
    nb_iterations = 500

    with open('examples/csplib/prob002_template_design.json', 'r') as json_file:
        data = json.load(json_file)

    problem_names = [problem['name'] for problem in data]

    tablesp_ortools =  PrettyTable(['Problem instance', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Branches'])
    tablesp_ortools.title = f'Results of the Template Design problem with CSE (average of {nb_iterations} iterations)'
    tablesp_ortools_noCSE =  PrettyTable(['Problem instance', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Branches'])
    tablesp_ortools_noCSE.title = f'Results of the Template Design problem without CSE (average of {nb_iterations} iterations)'

    for name in problem_names:
        # argument parsing
        url = "https://raw.githubusercontent.com/CPMpy/cpmpy/csplib/examples/csplib/prob002_template_design.json"
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
        print("Problem name:", problem_params["name"])

        def run_code(slvr):
            start_model_time = timeit.default_timer()
            model, (production, layout) = template_design(**problem_params)
            model_creation_time = timeit.default_timer() - start_model_time

            ret, transform_time, solve_time, num_branches = model.solve(solver=slvr)
            if ret:
                print("Solved this problem")
                return model_creation_time, transform_time, solve_time, num_branches
            else:
                print("Model is unsatisfiable!")
                return 404, 404, 404, 404
        
        for slvr in ["ortools_noCSE", "ortools"]:
            total_model_creation_time = 0
            total_transform_time = 0
            total_solve_time = 0
            total_execution_time = 0
            total_num_branches = 0

            for lp in range(nb_iterations):
                # Disable garbage collection for timing measurements
                gc.disable()

                # Measure the model creation and execution time
                start_time = timeit.default_timer()
                model_creation_time,transform_time, solve_time, num_branches = run_code(slvr)
                execution_time = timeit.default_timer() - start_time

                total_model_creation_time += model_creation_time
                total_transform_time += transform_time
                total_solve_time += solve_time
                total_execution_time += execution_time
                total_num_branches += num_branches

                # Re-enable garbage collection
                gc.enable()
            
            average_model_creation_time = total_model_creation_time / nb_iterations
            average_transform_time = total_transform_time / nb_iterations
            average_solve_time = total_solve_time / nb_iterations
            average_execution_time = total_execution_time / nb_iterations
            average_num_branches = total_num_branches / nb_iterations

            if slvr == 'ortools':
                tablesp_ortools.add_row([name, average_model_creation_time, average_transform_time, average_solve_time, average_execution_time, average_num_branches])
                with open("cpmpy/timing_results/template_design_CSE.txt", "w") as f:
                    f.write(str(tablesp_ortools))
                    f.write("\n")
            else:
                tablesp_ortools_noCSE.add_row([name, average_model_creation_time, average_transform_time, average_solve_time, average_execution_time, num_branches])
                with open("cpmpy/timing_results/template_design.txt", "w") as f:
                    f.write(str(tablesp_ortools_noCSE))
                    f.write("\n")
