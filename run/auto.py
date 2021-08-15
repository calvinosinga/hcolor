"""
Makes slice plots, computes auto correlations and auto power spectra
for a file.
"""

import sys
import os
import pickle
from hicc_library.results.auto import Auto


gd = pickle.load(open(os.getenv('PATHFILE'),'rb'))

INGRIDPATH = sys.argv[1]
OUTFILEPATH = sys.argv[2]

res = Auto(INGRIDPATH, OUTFILEPATH)

res.computeResults()
