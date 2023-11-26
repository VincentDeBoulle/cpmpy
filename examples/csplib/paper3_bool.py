import sys
sys.path.append('../cpmpy')

from cpmpy import *

A = boolvar()
B = boolvar()
C = boolvar()

model = Model()
model += A | B | C | True == True
model += B == False
model += B.implies(A)
model += A == True
print(model)
model.solve()
print("A: ", A.value())
print("B: ", B.value())
print("C: ", C.value())
