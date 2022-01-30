"""
Computes cross-correlations and cross-power
"""

import sys
import os
import pickle
import h5py as hp
from hc_lib.fields.field_super import Cross

gd = pickle.load(open(os.getenv('GDFILE'),'rb'))

if gd['verbose']:
    print("cross.py called, given the command-line arguments" + str(sys.argv))

INGRIDKEY1 = sys.argv[1]
INGRIDKEY2 = sys.argv[2]

INGRIDPATH1 = gd['grids'] + gd[INGRIDKEY1]
INGRIDPATH2 = gd['grids']+ gd[INGRIDKEY2]

pkl_paths = []
gridpaths = []
for g in (INGRIDPATH1, INGRIDPATH2):
    gridfile = hp.File(g, 'r')
    pkl_paths.append(gridfile['pickle'].attrs['path'])
    gridpaths.append(g)

field1 = pickle.load(open(pkl_paths[0], 'rb'))
field2 = pickle.load(open(pkl_paths[1], 'rb'))

try:
    OUTFILEPATH = gd['pickles'][field1.fieldname + 'X' + field2.fieldname]
except KeyError:
    print("didn't find key: %s"%(field1.fieldname + 'X' + field2.fieldname))
    OUTFILEPATH = gd['pickles'][field2.fieldname + 'X' + field1.fieldname]
    
if gd['verbose']:
    print('The first ingrid path:%s'%INGRIDPATH1)
    print('The second ingrid path:%s'%INGRIDPATH2)
    print('The outfile path:%s'%OUTFILEPATH)

res = Cross(field1, field2, gridpaths[0], gridpaths[1])
res.computeXpks()
res.computeXxis()
res.exportResultsToHdf5(OUTFILEPATH)
pickle.dump(res, open(OUTFILEPATH, 'wb'), pickle.HIGHEST_PROTOCOL)
