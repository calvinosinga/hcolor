#!/usr/bin/env python3

import sys
import numpy as np
import h5py as hp
from 

IN_GRID_BASE = sys.argv[1]
IN_START = sys.argv[2]
IN_STOP = sys.argv[3]
IN_STEP = sys.argv[4]
OUT_GRID = sys.argv[5]

infiles = [IN_GRID_BASE+'%d.hdf5'%i for i in range(IN_START, IN_STOP, IN_STEP)]
print("infiles:")
print(infiles)

def getKeys():
    f = hp
# load files

# combine grids

# save grids under first filename