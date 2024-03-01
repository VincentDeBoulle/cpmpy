"""
K4P2 Graceful Graph in cpmpy.

http://www.csplib.org/Problems/prob053/

A labelling f of the nodes of a graph with q edges is graceful if f assigns each node a unique label
from 0,1,...,q and when each edge xy is labelled with |f(x)-f(y)|, the edge labels are all different.
Gallian surveys graceful graphs, i.e. graphs with a graceful labelling, and lists the graphs whose status
is known.

All-Interval Series is a special case of a graceful graph where the graph is a line.

This cpmpy model was written by Hakan Kjellerstrand (hakank@gmail.com)
See also my cpmpy page: http://hakank.org/cpmpy/

Modified by Ignace Bleukx, ignace.bleukx@kuleuven.be
"""
import random
import sys
import psutil
import timeit
import gc
import numpy as np

sys.path.append('../cpmpy')

from cpmpy import *
from prettytable import PrettyTable

def gracefull_graphs(m,n,graph):
    graph = np.array(graph)

    model = Model()

    # variables
    nodes = intvar(0, m, shape=n, name="nodes")
    edges = intvar(1, m, shape=m, name="edges")

    # constraints
    model += np.abs(nodes[graph[:, 0]] - nodes[graph[:, 1]]) == edges

    model += (AllDifferent(edges))
    model += (AllDifferent(nodes))

    return model, (nodes, edges)


def get_data():
    # data
    m = 16
    n = 8

    graph = [[0, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3],
             [4, 5], [4, 6], [4, 7], [5, 6], [5, 7], [6, 7],
             [0, 4], [1, 5], [2, 6], [3, 7]]

    return m,n,graph

if __name__ == "__main__":
    
    nb_iterations = 10

    tablesp_ortools =  PrettyTable(['Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'number of search branches', 'Overall Memory Usage (Bytes)'])
    tablesp_ortools.title = 'Results of the gracefull graphs problem without CSE'
    tablesp_ortools_CSE =  PrettyTable(['Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'number of search branches', 'Overall Memory Usage (Bytes)'])
    tablesp_ortools_CSE.title = 'Results of the gracefull graphs problem with CSE' 
    tablesp_ortools_factor =  PrettyTable(['Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'number of search branches', 'Overall Memory Usage (Bytes)'])
    tablesp_ortools_factor.title = 'Results of the gracefull graphs problem' 

    # Set a random seed for reproducibility reasons
    random.seed(0)

    def run_code(slvr):
      start_model_time = timeit.default_timer()
      data = get_data()
      model, (nodes, edges) = gracefull_graphs(*data)
      model_creation_time = timeit.default_timer() - start_model_time
      return model.solve(solver=slvr), model_creation_time


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

                (_, transform_time, solve_time, num_branches), model_creation_time = run_code(slvr)
                
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

                tablesp_ortools.add_row([average_model_creation_time, average_transform_time, average_solve_time, average_execution_time, average_num_branches, average_mem_usage])
                with open("cpmpy/timing_results/gracefull_graphs.txt", "w") as f:
                    f.write(str(tablesp_ortools))
                    f.write("\n")
            elif slvr == 'ortools_CSE':
                average_model_creation_time_2 = sum(total_model_creation_time) / nb_iterations
                average_transform_time_2 = sum(total_transform_time) / nb_iterations
                average_solve_time_2 = sum(total_solve_time) / nb_iterations
                average_execution_time_2 = sum(total_execution_time) / nb_iterations 
                average_num_branches_2 = sum(total_num_branches) / nb_iterations
                average_mem_usage_2 = sum(total_mem_usage) / nb_iterations

                tablesp_ortools_CSE.add_row([average_model_creation_time_2, average_transform_time_2, average_solve_time_2, average_execution_time_2, average_num_branches_2, average_mem_usage_2])
                with open("cpmpy/timing_results/gracefull_graphs_CSE.txt", "w") as f:
                    f.write(str(tablesp_ortools_CSE))
                    f.write("\n")

                factor_model_creation_time = average_model_creation_time / average_model_creation_time_2
                factor_tranform_time = average_transform_time / average_transform_time_2
                factor_solve_time = average_solve_time / average_solve_time_2
                factor_execution_time = average_execution_time / average_execution_time_2
                factor_num_branches = average_num_branches / average_num_branches_2
                factor_mem_usage = average_mem_usage / average_mem_usage_2

                tablesp_ortools_factor.add_row([factor_model_creation_time, factor_tranform_time, factor_solve_time, factor_execution_time, factor_num_branches, factor_mem_usage])
                with open("cpmpy/CSE_results/gracefull_graphs.txt", "w") as f:
                    f.write(str(tablesp_ortools_factor))
                    f.write("\n")