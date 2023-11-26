import sys
sys.path.append('../cpmpy')

from cpmpy import *

A = intvar(1, 7)
B = intvar(1, 7)
C = intvar(1, 7)
D = intvar(1, 7)
E = intvar(1, 7)
F = intvar(1, 7)
G = intvar(1, 7)

model = Model()
#model += AllDifferent([A,B,C,D,E,F,G])
model += A + 0 == A
model += 2 + 2 + 1 == B
model += B + C - C + 1 == 6
model += B + 1 == 6
model += (A + C - D) * 0 == 0
model += A * 1 + B == A + B

print(model)
model.solve()
print("A: ", A.value())
print("B: ", B.value())
print("C: ", C.value())
print("D: ", D.value())
print("E: ", E.value())
print("F: ", F.value())
print("G: ", G.value())