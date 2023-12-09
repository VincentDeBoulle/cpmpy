import sys
sys.path.append('../cpmpy')

from cpmpy import *

A = boolvar()
B = boolvar()
C = boolvar()

model = Model()

model += ~A | ~B | C

model.solve()