import sys
sys.path.append('../cpmpy')

from cpmpy import *

model = Model()

A = intvar(0, 100)
B = intvar(0, 100)
C = intvar(0, 100)
D = intvar(0, 100)
E = intvar(0, 100)

model += A + B == C + D
model += A + B == 50

model.solve(solver='ortools_CSE')