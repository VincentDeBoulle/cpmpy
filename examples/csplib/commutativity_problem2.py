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

model += alldifferent([A, B, C, D, E, F, G])
model += (A + B == C)
model += ((B + A == C) & (A + D == E)) | (F - E == A)
model += ((E - B == C) | (D + A == B)) & (C + D == G)
model += (F - C == C) & (B + D == F)
model += ((A + B + D == G) & (D + C == G)) & (D + B == F)

model.solve()
print("A: ", A.value())
print("B: ", B.value())
print("C: ", C.value())
print("D: ", D.value())
print("E: ", E.value())
print("F: ", F.value())
print("G: ", G.value())