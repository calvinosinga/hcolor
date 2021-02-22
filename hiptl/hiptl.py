#!/usr/bin/env python3

import numpy as np
import h5py as hp
import sys
import MAS_library as masl

# defining constants
CHUNK = sys.argv[1]
MAS = sys.argv[2]
BASE = '/lustre/diemer/illustris/hih2/' 
HOME = '/lustre/cosinga/ptl99/'
SAVE = '/lustre/cosinga/hiptl_output/'
BOXSIZE = 75.0 #Mpc/h
h = .6774
grid = (2048,2048,2048)

# getting data
hih2file = hp.File(BASE+"hih2_particles_099."+CHUNK+".hdf5", 'r')
ptlfile = hp.File(HOME+"snap_099."+CHUNK+".hdf5", 'r')
mass = ptlfile['PartType0']['Masses'][:]*1e10/h #~50 MB, in solar masses
pos = ptlfile['PartType0']['CenterOfMass'][:]/1e3 # ~150 MB, Mpc/h
f_neut_h = hih2file['PartType0']['f_neutral_H'][:] #~100 MB
w = hp.File(SAVE+'hiptl_99.'+CHUNK+'.hdf5', 'w')

# loop over each model
models = ['GD14', 'GK11', 'K13', 'S14']
for m in models:
    field = np.zeros(grid, dtype=np.float32)

    # getting the HI mass data
    h2_frac = hih2file['PartType0']['f_mol_'+m][:] # ~100 MB
    masshi = (1-h2_frac)*f_neut_h*mass # ~100 MB

    # f_neut_h is negative where the model isn't defined, removing negative masses.
    masshi = np.where(masshi >= 0, masshi, np.zeros(masshi.shape, dtype=np.float32))
    masshi = masshi.astype('float32')

    # assigning them into the field using the Mass Assignment Scheme given
    masl.MA(pos,field,BOXSIZE,MAS,masshi)
    w.create_dataset(m, data=field, compression="gzip", compression_opts=9)
w.close()
