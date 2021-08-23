"""
Makes slice plots, computes auto correlations and auto power spectra
for a file.
"""

import sys
import os
import pickle
from hicc_library.results.auto import Auto


gd = pickle.load(open(os.getenv('GDFILE'),'rb'))

INGRIDKEY = sys.argv[1]
OUTFILEKEY = sys.argv[2]
PLOTDIRKEY = sys.argv[3]

if gd['verbose']:
    print("auto.py called, given the command-line arguments" + str(sys.argv))

INGRIDPATH = gd['grids'] + gd[INGRIDKEY]
OUTFILEPATH = gd['results']+ gd[OUTFILEKEY]
PLOTDIR = gd['plots']+gd[PLOTDIRKEY]

if gd['verbose']:
    print('The ingrid path:%s'%INGRIDPATH)
    print('The outfile path:%s'%OUTFILEPATH)
    print('The plots path:%s'%PLOTDIR)
res = Auto(INGRIDPATH, OUTFILEPATH, PLOTDIR)

res.computeResults()
