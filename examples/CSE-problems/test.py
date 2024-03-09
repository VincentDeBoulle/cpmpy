import sys

sys.path.append('../cpmpy')

from cpmpy import *

model = Model()

A = intvar(0, 10)
B = intvar(0, 10)
C = intvar(0, 10)
D = intvar(0, 10)
E = intvar(0, 10)
F = intvar(0, 10)

model += A + B == C + F
model += D + E == A + B

model.solve(solver="ortools_CSE")