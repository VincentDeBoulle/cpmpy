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
    tablesp_ortools = PrettyTable(['Board size', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Search Branches'])
    tablesp_ortools.title = 'OR-Tools: Results of the Peaceably Co-existing Armies of Queens problem with CSE (average of 10 iterations)'
    tablesp_ortools_noCSE =  PrettyTable(['Board size', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Search Branches'])
    tablesp_ortools_noCSE.title = 'OR-Tools: Results of the Peaceably Co-existing Armies of Queens problem without CSE (average of 10 iterations)'
    
    for sz in range(5, 11):
        n = sz # Size of the board
        print('Size: ', n)
        
        def run_code(slvr):
            start_model_time = timeit.default_timer()
            model, black_queens, white_queens = peaceable_queens(n)
            model_creation_time = timeit.default_timer() - start_model_time
            return model.solve(solver=slvr), model_creation_time, black_queens, white_queens
        
        for slvr in ['ortools_noCSE', 'ortools']:
            total_model_creation_time = 0
            total_transform_time = 0
            total_solve_time = 0
            total_execution_time = 0
            total_num_branches = 0

            for lp in range(10):
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
                
                total_model_creation_time += model_creation_time
                total_transform_time += transform_time
                total_solve_time += solve_time
                total_execution_time += execution_time
                total_num_branches += num_branches

            average_model_creation_time = total_model_creation_time / 10
            average_transform_time = total_transform_time / 10
            average_solve_time = total_solve_time / 10
            average_execution_time = total_execution_time / 10
            average_num_branches = total_num_branches / 10

            if slvr == 'ortools':
                tablesp_ortools.add_row([n, average_model_creation_time, average_transform_time, average_solve_time, average_execution_time, average_num_branches])
                with open("cpmpy/timing_results/peaceably_queens_CSE.txt", "w") as f:
                    f.write(str(tablesp_ortools))
                    f.write("\n")
            elif slvr == 'ortools_noCSE':
                tablesp_ortools_noCSE.add_row([n, average_model_creation_time, average_transform_time, average_solve_time, average_execution_time, num_branches])
                with open("cpmpy/timing_results/peaceably_queens.txt", "w") as f:
                    f.write(str(tablesp_ortools_noCSE))
                    f.write("\n")