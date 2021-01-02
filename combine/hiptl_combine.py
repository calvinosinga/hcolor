import zipfile as zf
import numpy as np
import h5py as hp
import sys
import os
BASE = '/lustre/cosinga/hiptl_output/'
START = sys.argv[1]
END = sys.argv[2]
files = np.arange(int(START), int(END))
SNAPSHOT = sys.argv[3]
STATUS = sys.argv[4]
total = np.zeros((4, 2048, 2048, 2048), dtype=np.float32)
logfile = open(BASE+"combine_test_log.txt",'w')
for i in files:
    logfile.write("unzipping file " + str(i)+"\n")
    rzip = zf.ZipFile(BASE + "hiptl_"+str(SNAPSHOT)+'.'+str(i)+'.hdf5.zip','r')
    rzip.extractall()
    rzip.close()
    logfile.write("unzipped file " + str(i)+"\n")
    logfile.write("at this point, the running total has size: " + str(sys.getsizeof(total))+"\n")
    logfile.write("now starting to add to running total:\n")
    if STATUS == 'delete':
        os.remove(BASE+"hiptl_"+str(SNAPSHOT)+'.'+str(i)+'.hdf5.zip')
    f = hp.File(BASE+"hiptl_"+str(SNAPSHOT)+'.'+str(i)+'.hdf5','r')
    logfile.write("the hdf5 file that got opened has size " + str(sys.getsizeof(f))+"\n")
    keys = list(f.keys())
    logfile.write("size of the array being added: "+ str(sys.getsizeof(f[keys[0]][:]))+"\n")
    for k in range(keys):
        total[k,:,:,:] += f[keys[k]][:]
    logfile.write("after adding, the running total has size: " + str(sys.getsizeof(total))+"\n")
    f.close()
w = hp.File(BASE+"hiptl_"+SNAPSHOT+'.'+START+'.'+END+'.hdf5','w')
for k in range(keys):
    w.create_dataset(keys[k], data=total[k,:,:,:])
w.close()