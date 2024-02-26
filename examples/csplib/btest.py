import sys

sys.path.append('../cpmpy')

from cpmpy import *

model = Model()

a = intvar(0, 10)
b = intvar(0, 10)

model += a + 1 + 2 + 3 - 6 == a 
model += a + b - a == 5

model.solve(solver="ortools_CSE")