import sys
sys.path.append('../cpmpy')

from cpmpy import *

model = Model()
A = intvar(0, 1000)
B = intvar(0, 1000)

model += A // A == B

print(model)