
import sys
sys.path.append('../cpmpy')

from cpmpy import *

A = intvar(1, 7)
B = intvar(1, 7)
C = intvar(1, 7)
D = intvar(1, 7)

model = Model()

model += 1 == A * B - C
print(model)
model.solve()