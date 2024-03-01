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
import argparse
import sys
import random
import psutil
import requests
import numpy as np
import gc
import timeit
import json

sys.path.append('../cpmpy')

from cpmpy import *
from prettytable import PrettyTable

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

    nb_iterations = 10

    with open('examples/csplib/prob002_template_design.json', 'r') as json_file:
        data = json.load(json_file)

    problem_names = [problem['name'] for problem in data]

    tablesp_ortools =  PrettyTable(['Problem instance', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Branches', 'Overall Memory Usage (Bytes)'])
    tablesp_ortools.title = 'Results of the Template Design problem without CSE'
    tablesp_ortools_CSE =  PrettyTable(['Problem instance', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Branches', 'Overall Memory Usage (Bytes)'])
    tablesp_ortools_CSE.title = 'Results of the Template Design problem with CSE'
    tablesp_ortools_factor =  PrettyTable(['Problem instance', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Branches', 'Overall Memory Usage (Bytes)'])
    tablesp_ortools_factor.title = 'Results of the Template Design problem'

    for name in problem_names:

        # Set a random seed for reproducibility reasons
        random.seed(0)

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

            ret, transform_time, solve_time, num_branches = model.solve(solver=slvr, time_limit=30)
            
            if ret:
                print("Solved this problem")
                return model_creation_time, transform_time, solve_time, num_branches
                
            elif model.status().runtime > 29:
                print("This problem passes the time limit")
                return 408, 408, 408, 408
            else:
                print("Model is unsatisfiable!")
                return 404, 404, 404, 404
        
        for slvr in ["ortools", "ortools_CSE"]:

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
                
                model_creation_time,transform_time, solve_time, num_branches = run_code(slvr)
                
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
                with open("cpmpy/timing_results/template_design.txt", "w") as f:
                    f.write(str(tablesp_ortools))
                    f.write("\n")

            elif slvr == 'ortools_CSE':
                average_model_creation_time_2 = sum(total_model_creation_time) / nb_iterations
                average_transform_time_2 = sum(total_transform_time) / nb_iterations
                average_solve_time_2 = sum(total_solve_time) / nb_iterations
                average_execution_time_2 = sum(total_execution_time) / nb_iterations 
                average_num_branches_2 = sum(total_num_branches) / nb_iterations
                average_mem_usage_2 = sum(total_mem_usage) / nb_iterations

                tablesp_ortools_CSE.add_row([name, average_model_creation_time_2, average_transform_time_2, average_solve_time_2, average_execution_time_2, average_num_branches_2, average_mem_usage_2])
                with open("cpmpy/timing_results/template_design_CSE.txt", "w") as f:
                    f.write(str(tablesp_ortools_CSE))
                    f.write("\n")

                factor_model_creation_time = average_model_creation_time / average_model_creation_time_2
                factor_tranform_time = average_transform_time / average_transform_time_2
                factor_solve_time = average_solve_time / average_solve_time_2
                factor_execution_time = average_execution_time / average_execution_time_2
                factor_num_branches = average_num_branches / average_num_branches_2
                factor_mem_usage = average_mem_usage / average_mem_usage_2

                tablesp_ortools_factor.add_row([name, factor_model_creation_time, factor_tranform_time, factor_solve_time, factor_execution_time, factor_num_branches, factor_mem_usage])
                with open("cpmpy/CSE_results/template_design.txt", "w") as f:
                    f.write(str(tablesp_ortools_factor))
                    f.write("\n")