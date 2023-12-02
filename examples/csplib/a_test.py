import sys
sys.path.append('../cpmpy')

from cpmpy import *

A = intvar(1, 70)
B = intvar(1, 70)
C = intvar(1, 70)
D = intvar(1, 70)
E = intvar(1, 70)
F = intvar(1, 70)
G = intvar(1, 70)

model = Model()

model += A + B + C == D
model += A * (A + B + C) == E

print(model)

model.solve()
print("A: ", A.value())
print("B: ", B.value())
print("C: ", C.value())
print("D: ", D.value())
print("E: ", E.value())
print("F: ", F.value())
print("G: ", G.value())