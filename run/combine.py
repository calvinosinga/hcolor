#!/usr/bin/env python3

import sys
import os
import numpy as np
import h5py as hp
import pickle
from hc_lib.grid.grid import Chunk, VelChunk

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
    # tells how the dataset should be combined
    operations = {}
    implemented_ops = ['sum', 'hist', 'extend']
    f = hp.File(infiles[0],'r')
    klist = list(f.keys())
    if gd['verbose']:
        print("keylist from %s"%infiles[0])
        print(klist)
    
    try:
        klist.remove('pickle')
        if gd['verbose']:
            print("removed pickle dataset...")
    except ValueError:
        pass
    
    # for each key, figure out which operation needs to be done.
    for k in klist:
        # by default, we sum. If this is a negative number, then check what operation is needed
        if f[k].attrs["combine"] < 0:
            try:
                operations[k] = f[k].attrs['operation']
            except KeyError:
                print('%s did not want combine, nor was an operation given'%k)
                operations[k] = None
            
            # now check that the given operation is implemented
            if not operations[k] in implemented_ops:
                raise NotImplementedError("%s that combine"%operations[k] + \
                        "operation is not implemented")
        else: # default operation
            operations[k] = 'sum'


    f.close()
    return klist, operations

def addPickle(w):
    f=hp.File(infiles[0],'r')
    dat = w.create_dataset('pickle', data=[0])
    dat.attrs['path'] = f['pickle'].attrs['path']
    f.close()
    return


keylist, ops = getKeys()
if gd['verbose']:
    print("\nThe datasets to be combined in the first file: ")
    print(keylist)


w = hp.File(outpath, 'w')
addPickle(w)

for k in range(len(keylist)):

    # sum the chunks
    if ops[keylist[k]] == 'sum':

        if gd['verbose']:
            print("summing datasets for %s"%keylist[k])
        
        f1 = hp.File(infiles[0], 'r')
        if 'vel' in keylist[k]:
            chunk1 = VelChunk.loadGrid(f1[keylist[k]], gd['verbose'])
        else:
            chunk1 = Chunk.loadGrid(f1[keylist[k]], gd['verbose'])

        for i in range(1,len(infiles)):
            try:
                f2 = hp.File(infiles[i],'r')
            except OSError:
                print("did not find file %s"%infiles[i])
            else:
                if isinstance(chunk1, VelChunk):
                    chunk2 = VelChunk.loadGrid(f2[keylist[k]], gd['verbose'])
                else:
                    chunk2 = Chunk.loadGrid(f2[keylist[k]], gd['verbose'])
                chunk1.combineChunks(chunk2)
        dat = chunk1.saveGrid(w)
        old_attrs = dict(f1[keylist[k]].attrs)
        for old_key in old_attrs:
            if old_key not in dict(dat.attrs):
                dat.attrs[old_key] = old_attrs[old_key]
    
    # sum the histograms
    elif ops[keylist[k]] == 'hist':

        if gd['verbose']:
            print("summing the histograms for %s"%keylist[k])
        
        f1 = hp.File(infiles[0], 'r')
        tot_hist = np.zeros_like(f1[keylist[k]][:], dtype=np.float32)
        tot_hist += f1[keylist[k]][:]
        tot_combine = f1[keylist[k]].attrs["combine"]
        for i in range(1, len(infiles)):
            try:
                f2 = hp.File(infiles[i], 'r')
            except OSError:
                print("did not find file %s"%infiles[i])
            else:
                tot_hist += f2[keylist[k]][:]
                if gd['verbose']:
                    print("running total for histogram:")
                    print(tot_hist)
        dat = w.create_dataset(keylist[k], data=tot_hist)
        dat.attrs["combine"] = f1[keylist[k]].attrs["combine"]
        dat.attrs["operation"] = f1[keylist[k]].attrs['operation']
        for old_key in old_attrs:
            if old_key not in dict(dat.attrs):
                dat.attrs[old_key] = old_attrs[old_key]
    # extend the datasets
    elif ops[keylist[k]] == 'extend':
        #TODO:
        continue

    
w.close()

# deleting the combine files to save space
for i in infiles:
    if os.path.exists(i):
        os.remove(i)
