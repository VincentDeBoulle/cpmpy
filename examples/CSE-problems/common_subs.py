import sys
import gc
import random
import timeit

sys.path.append('../cpmpy')

from cpmpy import *
from prettytable import PrettyTable

A = intvar(0, 1000)
B = intvar(0, 1000)
C = intvar(0, 1000)
D = intvar(0, 1000)
E = intvar(0, 1000)
F = intvar(0, 1000)
G = intvar(0, 1000)
H = intvar(0, 1000)
I = intvar(0, 1000)
J = intvar(1, 1000)
K = intvar(0, 1000)
L = intvar(0, 1000)

def common_subs():
    model = Model()

    model += A ** 2 == 10000
    model += A ** 2 == B + C
    model += B + C == D
    model += L + K == B + C
    model += I // J == D
    model += F * G * H == I // J

    return model

if __name__ == "__main__":
    nb_iterations = 10

    # Set random seed for same random conditions in both iterations
    random.seed(0)

    tablesp_ortools =  PrettyTable(['Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time'])
    tablesp_ortools.title = 'Results of the Permutations problem without CSE'
    tablesp_ortools_CSE =  PrettyTable(['Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time'])
    tablesp_ortools_CSE.title = 'Results of the Permutations problem with CSE'    
    tablesp_ortools_factor =  PrettyTable(['Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time'])
    tablesp_ortools_factor.title = 'Results of the Permutations problem'

    def create_model():
        return common_subs()
    model_creation_time = timeit.timeit(create_model, number = 1)    

    def run_code(slvr):
        start_model_time = timeit.default_timer()
        model = common_subs()
        model_creation_time = timeit.default_timer() - start_model_time
        return model.solve(solver=slvr, time_limit=30), model_creation_time

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

            tablesp_ortools.add_row([average_model_creation_time, average_transform_time, average_solve_time, average_execution_time])
            with open("cpmpy/timing_results/common_subs_z3.txt", "w") as f:
                f.write(str(tablesp_ortools))
                f.write("\n")

        elif slvr == 'z3_2':
            average_model_creation_time_2 = sum(total_model_creation_time) / nb_iterations
            average_transform_time_2 = sum(total_transform_time) / nb_iterations
            average_solve_time_2 = sum(total_solve_time) / nb_iterations
            average_execution_time_2 = sum(total_execution_time) / nb_iterations 

            tablesp_ortools_CSE.add_row([average_model_creation_time_2, average_transform_time_2, average_solve_time_2, average_execution_time_2])
            with open("cpmpy/timing_results/common_subs_z3_CSE.txt", "w") as f:
                f.write(str(tablesp_ortools_CSE))
                f.write("\n")

            factor_model_creation_time = average_model_creation_time / average_model_creation_time_2
            factor_tranform_time = average_transform_time / average_transform_time_2
            factor_solve_time = average_solve_time / average_solve_time_2
            factor_execution_time = average_execution_time / average_execution_time_2

            tablesp_ortools_factor.add_row([factor_model_creation_time, factor_tranform_time, factor_solve_time, factor_execution_time])
            with open("cpmpy/CSE_results/common_subs_z3.txt", "w") as f:
                f.write(str(tablesp_ortools_factor))
                f.write("\n")