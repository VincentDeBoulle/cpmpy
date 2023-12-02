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
model += 24 == C * (D * B * A)
model += ((((A + B) + C) + D) + (C + D)) == ((A + ((B + C) + D)) + (D + C))
model += A * B // C + D == D + B * A // C
model += (A * D * C) / B == (C * A * D) // B
model += A * B * C * D == D * B * A * C
model += A * B * C *D == D * C * B * A
model += (((A * B) * C) * D) == (A * ((B * C) * D))
model += ((((A + B) == C) & (D == 4)) & ((B + C == E) & ((A == 1) & (B == 2)))) & (B + A == C)

print(model)

model.solve()
print("A: ", A.value())
print("B: ", B.value())
print("C: ", C.value())
print("D: ", D.value())
print("E: ", E.value())
print("F: ", F.value())
print("G: ", G.value())
