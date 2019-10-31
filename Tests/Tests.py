import os
pardir = os.path.abspath(os.pardir).replace('\\','/')+'/'

comps = ['PyCQ/','PyGIS/','PyLib/','PyLSH/','PySZZ/']

import sys

for comp in comps:
    if not (pardir+comp in sys.path):
        sys.path.append(pardir+comp)

import unittest

from GIS_UnitTests import *

if __name__ == '__main__':
    unittest.main()