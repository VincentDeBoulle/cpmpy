import sys
sys.path.append('../cpmpy')

from cpmpy import *

A = boolvar()
B = boolvar()
C = boolvar()
D = boolvar()
E = intvar(1, 10)
F = intvar(1, 10)

model = Model()

model += ~A | ~B | C | D | (E > F)

model.solve(solver='ortools_CSE')