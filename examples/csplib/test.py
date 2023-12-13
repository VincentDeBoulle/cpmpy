import sys
sys.path.append('../cpmpy')
from cpmpy import *

model = Model()

A = intvar(0, 10)

model += A + 1 + 2 + 3 == 7

print(model)

model.solve()