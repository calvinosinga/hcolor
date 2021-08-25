"""
Computes cross-correlations and cross-power
"""

import sys
import os
import pickle
import h5py as hp
from hicc_library.fields.field_super import Cross

gd = pickle.load(open(os.getenv('GDFILE'),'rb'))

if gd['verbose']:
    print("cross.py called, given the command-line arguments" + str(sys.argv))

INGRIDKEY1 = sys.argv[1]
INGRIDKEY2 = sys.argv[2]
OUTFILEKEY = sys.argv[3]
PLOTDIRKEY = sys.argv[4]

INGRIDPATH1 = gd[INGRIDKEY1]
INGRIDPATH2 = gd[INGRIDKEY2]
OUTFILEPATH = gd[OUTFILEKEY]
PLOTDIR = gd[PLOTDIRKEY]

pkl_paths = []
keylists = []
gridfiles = []
for g in (INGRIDPATH1, INGRIDPATH2):
    gridfile = hp.File(g, 'r')
    pkl_paths = gridfile['pickle'].attrs['path']
    keylists.append(list(gridfile.keys()))
    gridfiles.append(gridfile)

field1 = pickle.load(open(pkl_paths[0], 'rb'))
field2 = pickle.load(open(pkl_paths[1], 'rb'))


if gd['verbose']:
    print('The first ingrid path:%s'%INGRIDPATH1)
    print('The second ingrid path:%s'%INGRIDPATH2)
    print('The outfile path:%s'%OUTFILEPATH)
    print('The plots path:%s'%PLOTDIR)

res = Cross(field1, field2, gridfiles[0], gridfiles[1])

pickle.dump(res, open(OUTFILEPATH, 'wb'), pickle.HIGHEST_PROTOCOL)

for i in gridfiles:
    i.close()
