import sys
sys.path.append('../cpmpy')
from cpmpy import *

model = Model()

A = intvar(0, 10)
B = intvar(0, 10)
C = intvar(0, 10)

model += A * 0 == 0
model += B - 0 + C + 0 == C + B
model += 0 // C == 0
model += 0 ** A == 0
model += A * 1 == A
model += A // 1 == A

print(model)

model.solve(solver="ortools_CSE")