import os
import sys


try:


    pardir = os.path.abspath(os.pardir).replace('\\','/')+'/'

    #comps = []#'PyCQ/','PyGIS/','PyLib/','PyLSH/','PySZZ/']

    import sys

    #for comp in comps:
    #    if not (pardir+comp in sys.path):
    #        sys.path.append(pardir+comp)
	
	sys.path.append(pardir)


    from app import app as application


except Exception as ex:
    file = open('error.txt','w')
    file.write(str(ex))
    file.close()
