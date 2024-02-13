"""
Peaceably co-existing armies of queens in CPMpy

CSPlib prob110
https://www.csplib.org/Problems/prob110/models/PeacableArmies.py.html

Problem description from CSPlib website:
In the "Armies of queens" problem, we are required to place two equal-sized armies
of black and white queens on a chessboard so that the white queens do not attack
the black queens (and necessarily visa versa) and to find the maximum size of the
two armies.

This CPMpy model was written by Vincent De Boulle
"""
# Add the correct path
import sys
sys.path.append('../cpmpy')

# Load the libraries
from cpmpy import *
import timeit
from prettytable import PrettyTable
import gc

def peaceable_queens(n=8):

    b = intvar(0, 1, shape=(n,n))
    w = intvar(0, 1, shape=(n,n))

    model = Model()

    num_black_queens = sum(b)
    num_white_queens = sum(w)

    model += (num_black_queens == num_white_queens)
    model.objective(num_black_queens, minimize=False)

    for bx in range(n):
        for by in range(n):
            for wx in range(n):
                for wy in range(n):
                    if (bx, by)  == (wx, wy):
                        model += b[bx][by] + w[wx][wy] <= 1
                    if bx < wx or (bx == wx and by < wy):
                        if bx == wx or by == wy or abs(bx - wx) == abs(by - wy):
                            model += b[bx][by] + w[wx][wy] <= 1
                            model += w[bx][by] + b[wx][wy] <= 1
    return model, b,w

if __name__ == "__main__":

    nb_iterations = 10

    tablesp_ortools = PrettyTable(['Board size', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Search Branches'])
    tablesp_ortools.title = 'Results of the Peaceably Co-existing Armies of Queens problem without CSE'
    tablesp_ortools_CSE =  PrettyTable(['Board size', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Search Branches'])
    tablesp_ortools_CSE.title = 'Results of the Peaceably Co-existing Armies of Queens problem with CSE'
    tablesp_ortools_factor =  PrettyTable(['Board size', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Search Branches'])
    tablesp_ortools_factor.title = 'Results of the Peaceably Co-existing Armies of Queens problem'
        
    for sz in range(5, 21):
        n = sz # Size of the board
        print('Size: ', n)
        
        def run_code(slvr):
            start_model_time = timeit.default_timer()
            model, black_queens, white_queens = peaceable_queens(n)
            model_creation_time = timeit.default_timer() - start_model_time
            return model.solve(solver=slvr), model_creation_time, black_queens, white_queens
        
        for slvr in ['ortools', 'ortools_CSE']:
            total_model_creation_time = []
            total_transform_time = []
            total_solve_time = []
            total_execution_time = []
            total_num_branches = []

            for lp in range(nb_iterations):
                gc.disable()

                start_time = timeit.default_timer()
                (n_sols, transform_time, solve_time, num_branches), model_creation_time, black_queens, white_queens = run_code(slvr)
                execution_time = timeit.default_timer() - start_time

                line = '+---'*n +'+\n'
                out = line
                for x in range(n):
                    for y in range(n):
                        if black_queens.value()[x][y] == 1:
                            out += '| B '
                        elif white_queens.value()[x][y] == 1:
                            out += '| W '
                        else:
                            out += '|   '
                    out += '|\n' + line
                print(out)
                
                total_model_creation_time.append(model_creation_time)
                total_transform_time.append(transform_time)
                total_solve_time.append(solve_time)
                total_execution_time.append(execution_time)
                total_num_branches.append(num_branches)

                gc.enable()

            if slvr == 'ortools':
                average_model_creation_time = sum(total_model_creation_time) / nb_iterations
                average_transform_time = sum(total_transform_time) / nb_iterations
                average_solve_time = sum(total_solve_time) / nb_iterations
                average_execution_time = sum(total_execution_time) / nb_iterations
                average_num_branches = sum(total_num_branches) / nb_iterations

                tablesp_ortools.add_row([n, average_model_creation_time, average_transform_time, average_solve_time, average_execution_time, average_num_branches])
                with open("cpmpy/timing_results/peaceably_queens.txt", "w") as f:
                    f.write(str(tablesp_ortools))
                    f.write("\n")
            if slvr == 'ortools_CSE':
                average_model_creation_time_2 = sum(total_model_creation_time) / nb_iterations
                average_transform_time_2 = sum(total_transform_time) / nb_iterations
                average_solve_time_2 = sum(total_solve_time) / nb_iterations
                average_execution_time_2 = sum(total_execution_time) / nb_iterations
                average_num_branches_2 = sum(total_num_branches) / nb_iterations

                tablesp_ortools_CSE.add_row([n, average_model_creation_time_2, average_transform_time_2, average_solve_time_2, average_execution_time_2, average_num_branches_2])
                with open("cpmpy/timing_results/peaceably_queens_CSE.txt", "w") as f:
                    f.write(str(tablesp_ortools_CSE))
                    f.write("\n")

                factor_model_creation_time = average_model_creation_time / average_model_creation_time_2
                factor_tranform_time = average_transform_time / average_transform_time_2
                factor_solve_time = average_solve_time / average_solve_time_2
                factor_execution_time = average_execution_time / average_execution_time_2
                factor_num_branches = average_num_branches / average_num_branches_2

                tablesp_ortools_factor.add_row([n, factor_model_creation_time, factor_tranform_time, factor_solve_time, factor_execution_time, factor_num_branches])
                with open("cpmpy/CSE_results/peaceably_queens.txt", "w") as f:
                    f.write(str(tablesp_ortools_factor))
                    f.write("\n")
