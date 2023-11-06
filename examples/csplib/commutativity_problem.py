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

model += AllDifferent([A, B, C, D, E, F, G])
model += B + A + C == F
model += A + B == C
model += B + A + D == G
model += G - E == B
model += D + C == E + B
model += C * B + B== G - A + B

model.solve()
print("A: ", A.value())
print("B: ", B.value())
print("C: ", C.value())
print("D: ", D.value())
print("E: ", E.value())
print("F: ", F.value())
print("G: ", G.value())