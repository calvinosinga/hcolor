#!/usr/bin/env python3

import sys
import os
import numpy as np
import h5py as hp
import pickle
from hicc_library.grid.grid import Chunk

IN_GRID = sys.argv[1]
IN_START = int(sys.argv[2])
IN_STOP = int(sys.argv[3])
IN_STEP = int(sys.argv[4])
OUT_GRID = sys.argv[5]

gd = pickle.load(open(os.getenv('PATHFILE'),'rb'))
inpath = gd[IN_GRID]
infiles = [inpath%i for i in range(IN_START, IN_STOP, IN_STEP)]
if gd['verbose']:
    print("infiles:")
    print(infiles)

def getKeys():
    f = hp.File(infiles[0],'r')
    return list(f.keys())

def setChunk(dataset):
    att = dict(dataset.attrs)
    ch = Chunk(att.pop('gridname'), att.pop('resolution'), att.pop('chunks'), dataset[:])
    ch.combine = att.pop('combine')
    return ch, att

keylist = getKeys()

print("The grids in the first file: ")
print(keylist)

w = hp.File(gd[OUT_GRID], 'w')

for k in range(len(keylist)):
    f1 = hp.File(infiles[0], 'r')
    chunk1, other_attrs = setChunk(f1[keylist[k]])
    for i in range(1,len(infiles)):
        f2 = hp.File(infiles[i],'r')
        chunk2 = setChunk(f2[keylist[k]])
        chunk1.combine(chunk2)
    dat = chunk1.saveGrid(w)
    dat.attrs.update(other_attrs)

# TODO: delete other grids