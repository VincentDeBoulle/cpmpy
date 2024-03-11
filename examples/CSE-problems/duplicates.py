import gc
import random
import sys
import timeit

from prettytable import PrettyTable
sys.path.append('../cpmpy')

from cpmpy import *

A = intvar(0, 100)
B = intvar(0, 100)
C = intvar(0, 100)
D = intvar(0, 100)
E = intvar(0, 100)
F = intvar(0, 100)


def duplicates(n= 10000):
    model = Model()

    model += A + B == 10
    model += A + B == C
    for i in range(n):
        model += A + B  == E + F
        model += C + D == A + B
    return model


if __name__ == "__main__":
    nb_iterations = 10

    tablesp_ortools =  PrettyTable(['Numbers of repetitions', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'number of search branches'])
    tablesp_ortools.title = 'Results of the Duplicates problem without CSE'
    tablesp_ortools_CSE =  PrettyTable(['Numbers of repetitions', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'number of search branches'])
    tablesp_ortools_CSE.title = 'Results of the Duplicates problem with CSE'    
    tablesp_ortools_factor =  PrettyTable(['Numbers of repetitions', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'number of search branches'])
    tablesp_ortools_factor.title = 'Results of the Duplicates problem'

    for n in range(1000, 10001, 500):

        print(f"n: {n}\n")

        def run_code(slvr):
            start_model_time = timeit.default_timer()
            model = duplicates(n)
            model_creation_time = timeit.default_timer() - start_model_time
            return model.solve(solver=slvr, time_limit=30), model_creation_time

        for slvr in ["ortools", "ortools_CSE"]:
            total_model_creation_time = []
            total_transform_time = []
            total_solve_time = []
            total_execution_time = []
            total_num_branches = []

            for lp in range(nb_iterations):
                random.seed(lp)

                # Disable garbage collection for timing measurements
                gc.disable()

                # Measure the model creation and execution time
                start_time = timeit.default_timer()
                (n_sols, transform_time, solve_time, num_branches), model_creation_time = run_code(slvr)
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

                tablesp_ortools.add_row([n, average_model_creation_time, average_transform_time, average_solve_time, average_execution_time, average_num_branches])
                with open("cpmpy/timing_results/duplicates.txt", "w") as f:
                    f.write(str(tablesp_ortools))
                    f.write("\n")

            elif slvr == 'ortools_CSE':
                average_model_creation_time_2 = sum(total_model_creation_time) / nb_iterations
                average_transform_time_2 = sum(total_transform_time) / nb_iterations
                average_solve_time_2 = sum(total_solve_time) / nb_iterations
                average_execution_time_2 = sum(total_execution_time) / nb_iterations 
                average_num_branches_2 = sum(total_num_branches) / nb_iterations

                tablesp_ortools_CSE.add_row([n, average_model_creation_time_2, average_transform_time_2, average_solve_time_2, average_execution_time_2, average_num_branches_2])
                with open("cpmpy/timing_results/duplicates.txt", "w") as f:
                    f.write(str(tablesp_ortools_CSE))
                    f.write("\n")

                factor_model_creation_time = average_model_creation_time / average_model_creation_time_2
                factor_tranform_time = average_transform_time / average_transform_time_2
                factor_solve_time = average_solve_time / average_solve_time_2
                factor_execution_time = average_execution_time / average_execution_time_2
                factor_num_branches = average_num_branches / average_num_branches_2

                tablesp_ortools_factor.add_row([n, factor_model_creation_time, factor_tranform_time, factor_solve_time, factor_execution_time, factor_num_branches])
                with open("cpmpy/CSE_results/duplicates.txt", "w") as f:
                    f.write(str(tablesp_ortools_factor))
                    f.write("\n")
