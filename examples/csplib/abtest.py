import sys

sys.path.append('../cpmpy')

from cpmpy import *

model = Model()

A = intvar(0, 1000)
B = intvar(0, 1000)
C = intvar(0, 1000)
D = intvar(0, 1000)
E = intvar(0, 1000)

model += (B + A)**2 == E


print(model)
model.solve(solver="ortools_CSE")