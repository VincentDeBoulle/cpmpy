import sys
sys.path.append('../cpmpy')
from cpmpy import *

model = Model()

A = intvar(0, 10)
B = intvar(0, 10)
C = intvar(0, 10)

model += A + C + 1 + 2 + 3 - A + B - B == 7

print(model)

model.solve()