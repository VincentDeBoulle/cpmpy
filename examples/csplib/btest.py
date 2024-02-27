import sys

sys.path.append('../cpmpy')

from cpmpy import *

model = Model()

#a = intvar(0, 10)
#b = intvar(0, 10)
#c = intvar(0, 10)
#d = intvar(0, 10)

#model += a + b == c + d
#model += a * c * d >= b
#model += a + 1 + 2 + 3 - 6 - a == a
#model += a + b - a == 5

A = boolvar()
B = boolvar()
C = boolvar()
D = boolvar()

model += (A & B) == D
model += (A & B) >= C 

model.solve(solver="ortools_CSE")
print(A.value())