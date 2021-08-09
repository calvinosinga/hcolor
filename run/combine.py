#!/usr/bin/env python3

import sys
import os
import numpy as np
import h5py as hp
from hicc_library.grid import Chunk

IN_GRID_BASE = sys.argv[1]
IN_START = int(sys.argv[2])
IN_STOP = int(sys.argv[3])
IN_STEP = int(sys.argv[4])
OUT_GRID = sys.argv[5]

paths = hp.File(os.getenv('PATHFILE'),'r')

infiles = [IN_GRID_BASE+'%d.hdf5'%i for i in range(IN_START, IN_STOP, IN_STEP)]
print("infiles:")
print(infiles)

def getKeys():
    f = hp.File(paths['grids']+infiles[0],'r')
    return list(f.keys())

def setChunk(dataset):
    att = dict(dataset.attrs)
    ch = Chunk(att['resolution'], att['chunks'], dataset[:])
    ch.combine = att['combine']
    return ch

keylist = getKeys()

print("The grids in the first file: ")
print(keylist)

w = hp.File(paths['grids']+OUT_GRID+'.hdf5', 'w')

for k in range(len(keylist)):
    f1 = hp.File(paths['grids']+infiles[0], 'r')
    chunk1 = setChunk(f1[keylist[k]])
    for i in range(1,len(infiles)):
        f2 = hp.File(paths['grids']+infiles[i],'r')
        chunk2 = setChunk(f2[keylist[k]])
        chunk1.combine(chunk2)
    chunk1.saveGrid(w)

# TODO: delete other grids