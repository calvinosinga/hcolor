import numpy as np
import h5py as hp
import sys
import zipfile as zf
import os

########## INPUTS #################
grid = (2048,2048,2048)
CHUNK = sys.argv[1]
LUM_MIN = -16 #detection minimum from Swanson
SNAPSHOT = sys.argv[2]
BOXSIZE = 75000 #kpc/h
HOME = '/lustre/cosinga/subhalo'+str(SNAPSHOT)+'/'
SAVE = '/lustre/cosinga/subhalo_output/'
def isred(gr, rband):#color definition as given in Swanson
    return gr> .9 - .03*(rband+23)
###################################
logfile = open(SAVE+'swanson_log'+str(SNAPSHOT)+'.txt', 'a')
try:
    f = hp.File(HOME+'fof_subhalo_tab_0'+str(SNAPSHOT)+'.'+str(CHUNK)+'.hdf5','r')
except IOError:
    logfile.write('failed to open file for '+str(CHUNK)+'\n')
else:
    try:
        pos = f['Subhalo']['SubhaloCM'] #kpc/h
        mass = f['Subhalo']['SubhaloMass']
        photo = f['Subhalo']['SubhaloStellarPhotometrics']
    except:
        logfile.write("chunk "+str(CHUNK)+ '\'s subhalo data was empty \n')
    else:
        redfield = np.zeros(grid, dtype=np.float32)
        bluefield = np.zeros(grid, dtype=np.float32)
        nondetfield = np.zeros(grid, dtype=np.float32)
        counts = np.zeros(3)
        edges = np.linspace(0,BOXSIZE, grid[0]-1) #definitions of bins
        bins = np.digitize(pos,edges)
        for j,b in enumerate(bins):
            rmag = photo[j][5]
            gmag = photo[j][4]
            if rmag<=LUM_MIN and isred(gmag-rmag,rmag):
                redfield[b[0],b[1],b[2]]+= mass[j]
                counts[2]+=1
            if rmag<=LUM_MIN and not isred(gmag-rmag,rmag):
                bluefield[b[0],b[1],b[2]]+= mass[j]
                counts[0]+=1
            if not rmag<=LUM_MIN:
                nondetfield[b[0],b[1],b[2]]+= mass[j]
                counts[1]+=1
        w = hp.File(SAVE+'swanson_'+str(SNAPSHOT)+'.'+str(CHUNK)+'.hdf5', 'w')
        w.create_dataset("red",data=redfield)
        w.create_dataset("blue",data=bluefield)
        w.create_dataset("nondetection",data=nondetfield)
        w.create_dataset('counts',data=counts)
        w.close()
        wzip = zf.ZipFile(SAVE+'swanson_'+str(SNAPSHOT)+'.'+str(CHUNK)+'.hdf5.zip', 'w')
        wzip.write(SAVE+'swanson_'+str(SNAPSHOT)+'.'+str(CHUNK)+'.hdf5', compress_type=zf.ZIP_DEFLATED)
        wzip.close()
        os.remove(SAVE+'swanson_'+str(SNAPSHOT)+'.'+str(CHUNK)+'.hdf5')


