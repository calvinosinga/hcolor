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

gd = pickle.load(open(os.getenv('GDFILE'),'rb'))
inpath = gd['grids'] + gd[IN_GRID]
infiles = [inpath%i for i in range(IN_START, IN_STOP, IN_STEP)]

if '%d' in gd[OUT_GRID]:
    outpath = gd['grids']+gd[OUT_GRID]%IN_START
else:
    outpath = gd['grids']+gd[OUT_GRID]

if gd['verbose']:
    print("infiles:")
    print(infiles)

    print("\n\noutput going to %s"%outpath)

def getKeys():
    f = hp.File(infiles[0],'r')
    return list(f.keys())

def setChunk(dataset):
    att = dict(dataset.attrs)
    ch = Chunk(att.pop('gridname'), att.pop('resolution'), att.pop('chunks'), 
            dataset[:], att.pop("combine"), att.pop("cicw_runtime"))
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
    for i in range(1,len(infiles)):
        try:
            f2 = hp.File(infiles[i],'r')
        except OSError:
            print("did not find file %s"%infiles[i])
        else:
            chunk2, att = setChunk(f2[keylist[k]])
            chunk1.combineChunks(chunk2)
    dat = chunk1.saveGrid(w)
    dat.attrs.update(other_attrs)
w.close()
# TODO: delete other grids, track combine_time