"""
Makes slice plots, computes auto correlations and auto power spectra
for a file.
"""

import sys
import os
import pickle
from hc_lib.grid.grid import Grid
from hc_lib.grid.grid_props import grid_props
import h5py as hp
from hc_lib.plots.result_lib import ResultLibrary


gd = pickle.load(open(os.getenv('GDFILE'),'rb'))

INGRIDKEY = sys.argv[1]

if gd['verbose']:
    print("auto.py called, given the command-line arguments" + str(sys.argv))

INGRIDPATH = gd['grids'] + gd[INGRIDKEY]

gridfile = hp.File(INGRIDPATH, 'r')
pkl_path = gridfile['pickle'].attrs['path']
field = pickle.load(open(pkl_path, 'rb'))

if gd['verbose']:
    print('The ingrid path:%s'%INGRIDPATH)
    print('The outfile path:%s'%pkl_path)

klist = list(gridfile.keys())
klist.remove('pickle')
for key in klist:
    if 'gridname' in dict(gridfile[key].attrs):
        grid = Grid.loadGrid(gridfile[key])
        gp = grid_props.loadProps(gridfile[key].attrs)
        if gp.props['type'] == 'mass':
            field.computePk(grid, gp)
            field.computeXi(grid, gp)
        else:
            field.computePk_theta(grid, gp)
            mass_key = key.replace('vel', 'mass', 1)
            try:
                mass_grid = Grid.loadGrid(gridfile[mass_key])
            except KeyError:
                print("unable to find mass grid for %s; mass key tried %s"%(key, mass_key))
            else:
                field.computeXpkdv(mass_grid, grid, gp)



pickle.dump(field, open(pkl_path, 'wb'), pickle.HIGHEST_PROTOCOL)

rlib = ResultLibrary(field.pkl_path + '_rlib.pkl')
rlib.addResults(field.getPks())
rlib.addResults(field.get2Dpks())
rlib.addResults(field.getXis())
pickle.dump(rlib, open(rlib.path, 'wb'), pickle.HIGHEST_PROTOCOL)

gridfile.close()
