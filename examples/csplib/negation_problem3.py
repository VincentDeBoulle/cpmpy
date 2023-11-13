import sys
sys.path.append('../cpmpy')

from cpmpy import *

A = boolvar()
B = boolvar()
C = boolvar()

model = Model()

model += ~(A & B & C)

print(model)
model.solve()

print("A: ", A.value())
print("B: ", B.value())