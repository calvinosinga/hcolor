"""
Makes slice plots, computes auto correlations and auto power spectra
for a file.
"""

import sys
import os
import pickle
from hicc_library.results.auto import Auto


gd = pickle.load(open(os.getenv('PATHFILE'),'rb'))

INGRIDKEY = sys.argv[1]
OUTFILEKEY = sys.argv[2]
PLOTDIRKEY = sys.argv[3]

INGRIDPATH = gd[INGRIDKEY]
OUTFILEPATH = gd[OUTFILEKEY]
PLOTDIR = gd[PLOTDIRKEY]

res = Auto(INGRIDPATH, OUTFILEPATH, PLOTDIR)

res.computeResults()
