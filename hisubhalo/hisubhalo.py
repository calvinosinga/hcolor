import numpy as np
import h5py as hp
import sys


########## INPUTS #################
grid = (2048,2048,2048)
SNAPSHOT = sys.argv[1]
BOXSIZE = 75000 #kpc/h
HOME = '/lustre/cosinga/subhalo'+str(SNAPSHOT)+'/'
SAVE = '/lustre/cosinga/subhalo_output/'

###################################
logfile = open(SAVE+'hisubhalo_log'+str(SNAPSHOT)+'.txt', 'a')
edges = np.linspace(0,BOXSIZE, grid[0]-1) #definitions of bins
w = hp.File(SAVE+'hisubhalo_'+str(SNAPSHOT)+'.final.hdf5', 'w')
f = hp.File(HOME+'hih2_galaxy_0'+str(SNAPSHOT)+'.'+str(i)+'.hdf5','r')
idfile = hp.File(HOME+"id_pos"+str(SNAPSHOT)+".hdf5",'r')
pos = idfile['coordinates'][:]
keys = list(f.keys())
models = []
for k in keys:
    if 'm_hi' in k:
        models.append(k)
logfile.write("the models used are: "+str(models)+'\n')
bins = np.digitize(pos,edges)
for m in models:
    field = np.zeros(grid, dtype=np.float32)
    mass = f[m][:]
    for j,b in enumerate(bins):
        field[b[0],b[1],b[2]] += mass[j]
    w.create_dataset(m, data=field, compression="gzip", compression_opts=9)

w.close()
