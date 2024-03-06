import sys
sys.path.append('../cpmpy')
from cpmpy import *

model = Model()

A = intvar(1, 10)
B = intvar(1, 10)
C = intvar(1, 10)

model += A * 0 == 0
model += B - 0 + C + 0 == C + B
model += 0 // C == 0
model += 0 ** A == 0
model += 1 ** B == 1
model += A ** 1 == A
model += A * 1 == A
model += A // 1 == A

print(model)

model.solve(solver="ortools_CSE")