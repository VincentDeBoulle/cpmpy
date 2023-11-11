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
model += ((C + B) + (A + D) != C)
model += (-((C + B) + (A + D)) != C)
model += (-(A + C + D + B) != -(A * B * D))
#model += (B + A != C)

print("model: ", model)
print("\n")
model.solve()


print("A: ", A.value())
print("B: ", B.value())
print("C: ", C.value())