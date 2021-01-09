from Pk_library import XPk
import sys
import numpy as np
import h5py as hp

HOME='/lustre/cosinga/final_fields/'
firstfile = sys.argv[1]
firstfield = sys.argv[2]
secondfile = sys.argv[3]
secondfield = sys.argv[4]
savename = sys.argv[5]
BOXSIZE = 75000.0 #kpc/h
grid = (2048, 2048, 2048)
f = hp.File(HOME+firstfile, 'r')
g = hp.File(HOME+secondfile, 'r')

