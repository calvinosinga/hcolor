#!/usr/bin/env python3

import sys
import os
from h5py._hl import attrs
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
inpath = gd['grids'] + gd[IN_GRID]
infiles = [inpath%i for i in range(IN_START, IN_STOP, IN_STEP)]

outpath = gd['grids']+gd[OUT_GRID]%IN_START
if gd['verbose']:
    print("infiles:")
    print(infiles)

    print("\n\noutput going to %s"%outpath)

def getKeys():
    f = hp.File(infiles[0],'r')
    return list(f.keys())

def setChunk(dataset):
    att = dict(dataset.attrs)
    ch = Chunk(att.pop('gridname'), att.pop('resolution'), att.pop('chunks'), dataset[:], att.pop("combine"))
    return ch, att

keylist = getKeys()
if gd['verbose']:
    print("\nThe grids in the first file: ")
    print(keylist)

w = hp.File(outpath, 'w')

for k in range(len(keylist)):
    if gd['verbose']:
        print("\ncombining chunks for %s"%keylist[k])
    f1 = hp.File(infiles[0], 'r')
    chunk1, other_attrs = setChunk(f1[keylist[k]])
    print(chunk1)
    print(other_attrs)
    for i in range(1,len(infiles)):
        f2 = hp.File(infiles[i],'r')
        print(chunk1)
        chunk2, att = setChunk(f2[keylist[k]])
        print(chunk1)
        chunk1.combine(chunk2)
    dat = chunk1.saveGrid(w)
    dat.attrs.update(other_attrs)

# TODO: delete other grids