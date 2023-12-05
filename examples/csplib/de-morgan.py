import sys
sys.path.append('../cpmpy')

from cpmpy import *

A = boolvar()
B = boolvar()
C = boolvar()
D = boolvar()

model = Model()

#model += ~A | ~B 
#model += ~ (A & B) 
#model += (A & B)
model += ~(A | B)
model += ~A & ~B
model += (A | B) & ~C
model += (B | A) & D
model += ~(A | B)
model += B | A
model += ~A & ~B

print(model)
model.solve()

print(A.value())
print(B.value())