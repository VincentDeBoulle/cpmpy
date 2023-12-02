import sys
sys.path.append('../cpmpy')

from cpmpy import *

A = intvar(0, 7)
B = intvar(0, 7)
C = intvar(0, 7)
D = intvar(0, 7)
E = intvar(0, 7)
F = intvar(0, 7)
G = intvar(0, 7)

model = Model()

model += 0 ** A == B

print(model)

model.solve()
print("A: ", A.value())
print("B: ", B.value())
print("C: ", C.value())
print("D: ", D.value())
print("E: ", E.value())
print("F: ", F.value())
print("G: ", G.value())