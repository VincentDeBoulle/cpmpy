import sys
sys.path.append('../cpmpy')

from cpmpy import *

A = boolvar()
B = boolvar()
C = boolvar()
D = boolvar()
E = boolvar()
model = Model()

model += ~(A & B) == E
#model += ~A | ~B == E
#model += ~(A) |  ~(B) == D

print(model)
model.solve()

print("A: ", A.value())
print("B: ", B.value())
print("C: ", C.value())
print("D: ", D.value())
print("E: ", E.value())