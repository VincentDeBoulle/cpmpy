import sys
sys.path.append('../cpmpy')

from cpmpy import *

model = Model()
A = intvar(0, 1000)
B = intvar(0, 1000)
C = intvar(0, 1000)

model += C + A - A == B

print(model)