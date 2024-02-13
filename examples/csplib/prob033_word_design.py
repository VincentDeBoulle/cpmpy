"""
Word design in CPMpy

Problem 033 on CSPlib
https://www.csplib.org/Problems/prob033/

Problem: find as large a set S of strings (words) of length 8 over the alphabet W = { A,C,G,T } with the following properties:

Each word in S has 4 symbols from { C,G };
Each pair of distinct words in S differ in at least 4 positions; and
Each pair of words x and y in S (where x and y may be identical) are such that xR and yC differ in at least 4 positions. Here, ( x1,…,x8 )R = ( x8,…,x1 ) is the reverse of ( x1,…,x8 ) and ( y1,…,y8 )C is the Watson-Crick complement of ( y1,…,y8 ), i.e. the word where each A is replaced by a T and vice versa and each C is replaced by a G and vice versa.

Model created by Ignace Bleukx, ignace.bleukx@kuleuven.be
"""
import sys
import numpy as np
import timeit
from prettytable import PrettyTable
import gc

sys.path.append('../cpmpy')

from cpmpy import *
from cpmpy.expressions.utils import all_pairs

def word_design(n=2):
    A, C, G, T = 1, 2, 3, 4

    # words[i,j] is the j'th letter of the i'th word
    words = intvar(A, T, shape=(n, 8), name="words")

    model = Model()

    # 4 symbols from {C,G}
    for w in words:
        model += sum((w == C) | (w == G)) >= 4

    # each pair of distinct words differ in at least 4 positions
    for x,y in all_pairs(words):
        model += (sum(x != y) >= 4)

    for y in words:
        y_c = 5 - y  # Watson-Crick complement
        for x in words:
            # x^R and y^C differ in at least 4 positions
            x_r = x[::-1]  # reversed x
            model += sum(x_r != y_c) >= 4

    # break symmetry
    for r in range(n - 1):
        b = boolvar(n + 1)
        model += b[0] == 1
        model += b == ((words[r] <= words[r + 1]) &
                       ((words[r] < words[r + 1]) | b[1:] == 1))
        model += b[-1] == 0

    return model, (words,)

if __name__ == "__main__":
    import argparse

    nb_iterations = 10

    tablesp_ortools =  PrettyTable(['Number of words to find', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'number of search branches'])
    tablesp_ortools.title = 'Results of the Word Design problem without CSE'
    tablesp_ortools_CSE =  PrettyTable(['Number of words to find', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'number of search branches'])
    tablesp_ortools_CSE.title = 'Results of the Word Design problem with CSE'    
    tablesp_ortools_factor =  PrettyTable(['Number of words to find', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'number of search branches'])
    tablesp_ortools_factor.title = 'Results of the Word Design problem'

    for nb in range(10, 30, 2):
        parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("-n_words", type=int, default=nb, help="Number of words to find")

        n = parser.parse_args().n_words
        print(n)

        def run_code(slvr):
            start_model_time = timeit.default_timer()
            model, (words,) = word_design(n)
            model_creation_time = timeit.default_timer() - start_model_time
            return model.solve(solver=slvr), model_creation_time
        
        for slvr in ["ortools", "ortools_CSE"]:
            total_model_creation_time = []
            total_transform_time = []
            total_solve_time = []
            total_execution_time = []
            total_num_branches = []

            for lp in range(nb_iterations):
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
                with open("cpmpy/timing_results/word_design.txt", "w") as f:
                    f.write(str(tablesp_ortools))
                    f.write("\n")

            elif slvr == 'ortools_CSE':
                average_model_creation_time_2 = sum(total_model_creation_time) / nb_iterations 
                average_transform_time_2 = sum(total_transform_time) / nb_iterations
                average_solve_time_2 = sum(total_solve_time) / nb_iterations
                average_execution_time_2 = sum(total_execution_time) / nb_iterations
                average_num_branches_2 = sum(total_num_branches) / nb_iterations

                tablesp_ortools_CSE.add_row([n, average_model_creation_time_2, average_transform_time_2, average_solve_time_2, average_execution_time_2, average_num_branches_2])
                with open("cpmpy/timing_results/word_design_CSE.txt", "w") as f:
                    f.write(str(tablesp_ortools_CSE))
                    f.write("\n")
           
                factor_model_creation_time = average_model_creation_time / average_model_creation_time_2
                factor_tranform_time = average_transform_time / average_transform_time_2
                factor_solve_time = average_solve_time / average_solve_time_2
                factor_execution_time = average_execution_time / average_execution_time_2
                factor_num_branches = average_num_branches / average_num_branches_2

                tablesp_ortools_factor.add_row([n, factor_model_creation_time, factor_tranform_time, factor_solve_time, factor_execution_time, factor_num_branches])
                with open("cpmpy/CSE_results/word_design.txt", "w") as f:
                    f.write(str(tablesp_ortools_factor))
                    f.write("\n")