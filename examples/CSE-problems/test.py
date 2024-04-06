import sys

sys.path.append('../cpmpy')

from cpmpy import *

model = Model()

A = intvar(0, 1000)
B = intvar(0, 1000)
C = intvar(0, 1000)
D = intvar(0, 1000)
E = intvar(0, 1000)
F = intvar(0, 1000)

model += A * B + A * C == D
model += F + E == A * B

model.solve(solver='z3_2')