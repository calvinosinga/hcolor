import zipfile as zf
import numpy as np
import h5py as hp
import sys
import os
BASE = '/lustre/cosinga/hiptl_output/'
START = sys.argv[1]
END = sys.argv[2]
files = np.arange(START, END)
SNAPSHOT = sys.argv[3]
STATUS = sys.argv[4]
total = np.zeros((4, 2048, 2048, 2048), dtype=np.float32)
for i in files:
    rzip = zf.ZipFile(BASE + "hiptl_"+str(SNAPSHOT)+'.'+str(i)+'.hdf5.zip','r')
    rzip.extractall(BASE)
    rzip.close()
    if STATUS == 'delete':
        os.remove(BASE+"hiptl_"+str(SNAPSHOT)+'.'+str(i)+'.hdf5.zip')
    f = hp.File(BASE+"hiptl_"+str(SNAPSHOT)+'.'+str(i)+'.hdf5','r')
    keys = list(f.keys())
    for k in range(keys):
        total[k,:,:,:] += f[keys[k]][:]
    f.close()
