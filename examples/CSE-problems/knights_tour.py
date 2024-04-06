import sys
import gc
import random
import timeit

sys.path.append('../cpmpy')

from cpmpy import *
from prettytable import PrettyTable


def knights_tour(n):
    model = Model()

    tour = intvar(1, n, shape=n)

    for i in range(n):
        for j in range(n):
            if (abs(i - j) == 1):
                model += (tour[i] % n != tour[j] % n)

    return model

if __name__ == "__main__":

    nb_iterations = 1

    tablesp_ortools =  PrettyTable(['Size of n', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time'])
    tablesp_ortools.title = 'Results of the Knights Tour problem without CSE'
    tablesp_ortools_CSE =  PrettyTable(['Size of n', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time'])
    tablesp_ortools_CSE.title = 'Results of the Knights Tour problem with CSE'    
    tablesp_ortools_factor =  PrettyTable(['Size of board', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time'])
    tablesp_ortools_factor.title = 'Results of the Knights Tour problem'


    for n in range(5, 6, 100):

        def run_code(slvr):
            start_model_time = timeit.default_timer()
            model = knights_tour(n)
            model_creation_time = timeit.default_timer() - start_model_time
            return model.solve(solver=slvr), model_creation_time
        
        for slvr in ["z3", "z3_2"]:
            total_model_creation_time = []
            total_transform_time = []
            total_solve_time = []
            total_execution_time = []

            for lp in range(nb_iterations):
                random.seed(lp)

                # Disable garbage collection for timing measurements
                gc.disable()

                # Measure the model creation and execution time
                start_time = timeit.default_timer()
                (n_sols, transform_time, solve_time), model_creation_time = run_code(slvr)
                execution_time = timeit.default_timer() - start_time

                total_model_creation_time.append(model_creation_time)
                total_transform_time.append(transform_time)
                total_solve_time.append(solve_time)
                total_execution_time.append(execution_time)

                # Re-enable garbage collection
                gc.enable()

            if slvr == 'z3':
                average_model_creation_time = sum(total_model_creation_time) / nb_iterations 
                average_transform_time = sum(total_transform_time) / nb_iterations
                average_solve_time = sum(total_solve_time) / nb_iterations 
                average_execution_time = sum(total_execution_time) / nb_iterations 

                tablesp_ortools.add_row([n, average_model_creation_time, average_transform_time, average_solve_time, average_execution_time])
                with open("cpmpy/timing_results/knights_tour_z3.txt", "w") as f:
                    f.write(str(tablesp_ortools))
                    f.write("\n")

            elif slvr == 'z3_2':
                average_model_creation_time_2 = sum(total_model_creation_time) / nb_iterations
                average_transform_time_2 = sum(total_transform_time) / nb_iterations
                average_solve_time_2 = sum(total_solve_time) / nb_iterations
                average_execution_time_2 = sum(total_execution_time) / nb_iterations 

                tablesp_ortools_CSE.add_row([n, average_model_creation_time_2, average_transform_time_2, average_solve_time_2, average_execution_time_2])
                with open("cpmpy/timing_results/knights_tour_z3_CSE.txt", "w") as f:
                    f.write(str(tablesp_ortools_CSE))
                    f.write("\n")

                factor_model_creation_time = average_model_creation_time / average_model_creation_time_2
                factor_tranform_time = average_transform_time / average_transform_time_2
                factor_solve_time = average_solve_time / average_solve_time_2
                factor_execution_time = average_execution_time / average_execution_time_2

                tablesp_ortools_factor.add_row([n, factor_model_creation_time, factor_tranform_time, factor_solve_time, factor_execution_time])
                with open("cpmpy/CSE_results/knights_tour_z3.txt", "w") as f:
                    f.write(str(tablesp_ortools_factor))
                    f.write("\n")
