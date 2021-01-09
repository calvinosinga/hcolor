import numpy as np
import h5py as hp
import sys
CHUNK = sys.argv[1]
BASE = '/lustre/diemer/illustris/hih2/' 
HOME = '/lustre/cosinga/ptl99/'
SAVE = '/lustre/cosinga/hiptl_output/'
BOXSIZE = 75000 #kpc/h
grid = (2048,2048,2048)
fileno = 448
field = np.zeros(grid, dtype=np.float32) # 35 GB
edges = np.linspace(0,BOXSIZE,grid[0]-1)
hih2file = hp.File(BASE+"hih2_particles_099."+CHUNK+".hdf5", 'r')
ptlfile = hp.File(HOME+"snap_099."+CHUNK+".hdf5", 'r')
mass = ptlfile['PartType0']['Masses'][:] #~50 MB
pos = ptlfile['PartType0']['CenterOfMass'][:] # ~150 MB
f_neut_h = hih2file['PartType0']['f_neutral_H'][:] #~100 MB
models = ['GD14', 'GK11', 'K13', 'S14']
w = hp.File(SAVE+'hiptl_99.'+CHUNK+'.hdf5', 'w')
bins = np.digitize(pos, edges) # ~300 MB
for m in models:
    h2_frac = hih2file['PartType0']['f_mol_'+m][:] # ~100 MB
    masshi = (1-h2_frac)*f_neut_h*mass # ~100 MB
    masshi = masshi.astype('float32')# decreases size by 50 MB
    for ptl,b in enumerate(bins):
        field[b[0],b[1],b[2]] += masshi[ptl]
    w.create_dataset(m, data=field, compression="gzip", compression_opts=9)
w.close()
