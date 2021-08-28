"""
Makes slice plots, computes auto correlations and auto power spectra
for a file.
"""

import sys
import os
import pickle
from hicc_library.grid.grid import Grid
import h5py as hp


gd = pickle.load(open(os.getenv('GDFILE'),'rb'))

INGRIDKEY = sys.argv[1]
OUTFILEKEY = sys.argv[2]
PLOTDIRKEY = sys.argv[3]

if gd['verbose']:
    print("auto.py called, given the command-line arguments" + str(sys.argv))

INGRIDPATH = gd['grids'] + gd[INGRIDKEY]
OUTFILEPATH = gd['results']+ gd[OUTFILEKEY]
PLOTDIR = gd[PLOTDIRKEY]

gridfile = hp.File(INGRIDPATH, 'r')
pkl_path = gridfile['pickle'].attrs['path']
field = pickle.load(open(pkl_path, 'rb'))

if gd['verbose']:
    print('The ingrid path:%s'%INGRIDPATH)
    print('The outfile path:%s'%OUTFILEPATH)
    print('The plots path:%s'%PLOTDIR)

klist = list(gridfile.keys())
klist.remove('pickle')
for key in klist:
    grid = Grid.loadGrid(gridfile[key])
    field.computePk(grid)
    field.computeXi(grid)
    field.makeSlice(grid)

pickle.dump(field, open(OUTFILEPATH, 'wb'), pickle.HIGHEST_PROTOCOL)
gridfile.close()
