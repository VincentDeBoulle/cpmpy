"""
Problem 026 on CSPLib
Sport scheduling in CPMpy

Model created by Ignace Bleukx
"""
import pandas as pd

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

    tablesp = PrettyTable(['Nb of Teams', 'Model Creation Time', 'Solver Creation + Transform Time', 'Solve Time', 'Overall Execution Time', 'Number of Branches'])

    for nb in range(2,21,2):
        print('\n number: {}'.format(nb))
        parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument("-n_teams", type=int, default=nb, help="Number of teams to schedule")

        args = parser.parse_args()

        n_teams = args.n_teams
        n_weeks, n_periods, n_matches = n_teams - 1, n_teams // 2, (n_teams - 1) * n_teams // 2

        def create_model():
            return sport_scheduling(n_teams)
        
        model_creation_time = timeit.timeit(create_model, number=1)

        def run_code():
            model, (home, away) = create_model()
            ret, transform_time, solve_time, num_branches = model.solve(time_limit=30)
            return transform_time, solve_time, num_branches
        
        execution_time = timeit.timeit(run_code, number=1)
        transform_time, solve_time, num_branches = run_code()

        tablesp.add_row([nb, model_creation_time, transform_time, solve_time, execution_time, num_branches])

        with open("cpmpy/timing_results/sport_scheduling.txt", "w") as f:
            f.write(str(tablesp))
            f.write("\n")
