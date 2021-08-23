"""
Computes cross-correlations and cross-power
"""

import sys
import os
import pickle
from hicc_library.results.cross import Cross


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

if gd['verbose']:
    print('The first ingrid path:%s'%INGRIDPATH1)
    print('The second ingrid path:%s'%INGRIDPATH2)
    print('The outfile path:%s'%OUTFILEPATH)
    print('The plots path:%s'%PLOTDIR)

res = Cross(INGRIDPATH1, INGRIDPATH2, OUTFILEPATH, PLOTDIR)

res.computeResults()
