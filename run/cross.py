"""
Computes cross-correlations and cross-power
"""

import sys
import os
import pickle
from hicc_library.results.cross import Cross


gd = pickle.load(open(os.getenv('GDFILE'),'rb'))

INGRIDKEY1 = sys.argv[1]
INGRIDKEY2 = sys.argv[2]
OUTFILEKEY = sys.argv[3]
PLOTDIRKEY = sys.argv[4]

INGRIDPATH1 = gd[INGRIDKEY1]
INGRIDPATH2 = gd[INGRIDKEY2]
OUTFILEPATH = gd[OUTFILEKEY]
PLOTDIR = gd[PLOTDIRKEY]

res = Cross(INGRIDPATH1, INGRIDPATH2, OUTFILEPATH, PLOTDIR)

res.computeResults()
