"""
Problem 026 on CSPLib
Sport scheduling in CPMpy

Model created by Ignace Bleukx
"""
import pandas as pd
import gc
import sys

from prettytable import PrettyTable

sys.path.append('../cpmpy')

from cpmpy import *
from cpmpy.expressions.utils import all_pairs

import numpy as np
import timeit

def sport_scheduling(n_teams):

    n_weeks, n_periods, n_matches = n_teams - 1, n_teams // 2, (n_teams - 1) * n_teams // 2

    home = intvar(1,n_teams, shape=(n_weeks, n_periods), name="home")
    away = intvar(1,n_teams, shape=(n_weeks, n_periods), name="away")

    model = Model()

    # teams cannot play each other
    model += home != away

    # every teams plays once a week
    # can be written cleaner, see issue #117
    # model += AllDifferent(np.append(home, away, axis=1), axis=0)
    for w in range(n_weeks):
        model += AllDifferent(np.append(home[w], away[w]))

    # every team plays each other
    for t1, t2 in all_pairs(range(1,n_teams+1)):
        model += (sum((home == t1) & (away == t2)) + sum((home == t2) & (away == t1))) >= 1

    # every team plays at most twice in the same period
    for t in range(1, n_teams + 1):
        # can be written cleaner, see issue #117
        # sum((home == t) | (away == t), axis=1) <= 2
        for p in range(n_periods):
            model += sum((home[p] == t) | (away[p] == t)) <= 2

    return model, (home, away)

if __name__ == "__main__":
    import argparse

    nb_iterations = 100

    tablesp = PrettyTable(['Nb of Teams', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Branches'])
    tablesp_ortools =  PrettyTable(['Nb of Teams', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Branches'])
    tablesp_ortools.title = f'Results of the Sport Scheduling problem with CSE (average of {nb_iterations} iterations)'
    tablesp_ortools_noCSE =  PrettyTable(['Nb of Teams', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Branches'])
    tablesp_ortools_noCSE.title = f'Results of the Sport Scheduling problem without CSE (average of {nb_iterations} iterations)'    

    for nb in range(8,21,2):
        print('\n number: {}'.format(nb))
        parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("-n_teams", type=int, default=nb, help="Number of teams to schedule")

        args = parser.parse_args()

        n_teams = args.n_teams
        n_weeks, n_periods, n_matches = n_teams - 1, n_teams // 2, (n_teams - 1) * n_teams // 2

        def create_model():
            return sport_scheduling(n_teams)
        
        def run_code(slvr):
            start_model_time = timeit.default_timer()
            model, (home, away) = sport_scheduling(n_teams)
            model_creation_time = timeit.default_timer() - start_model_time
            ret, transform_time, solve_time, num_branches = model.solve(solver=slvr, time_limit=30)
            return model_creation_time, transform_time, solve_time, num_branches
        
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
                model_creation_time, transform_time, solve_time, num_branches = run_code(slvr)
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
                tablesp_ortools.add_row([nb, average_model_creation_time, average_transform_time, average_solve_time, average_execution_time, average_num_branches])
                with open("cpmpy/timing_results/sport_scheduling_CSE.txt", "w") as f:
                    f.write(str(tablesp_ortools))
                    f.write("\n")
            else:
                tablesp_ortools_noCSE.add_row([nb, average_model_creation_time, average_transform_time, average_solve_time, average_execution_time, num_branches])
                with open("cpmpy/timing_results/sport_scheduling.txt", "w") as f:
                    f.write(str(tablesp_ortools_noCSE))
                    f.write("\n")
