import numpy as np
import h5py as hp
import sys
import os
BASE = '/lustre/cosinga/hiptl_output/'
START = sys.argv[1]
END = sys.argv[2]
filenos = np.arange(int(START), int(END))
SNAPSHOT = sys.argv[3]

logfile = open(BASE+"combine_test_log.txt",'w')
w = hp.File(BASE+"hiptl_"+SNAPSHOT+'.'+START+'.'+END+'.hdf5','w')
models = ['GD14', 'GK11', 'K13', 'S14']
files = ['hiptl_'+str(SNAPSHOT)+'.'+str(i)+'.hdf5' for i in filenos]
for m in models:
    total = np.zeros((2048, 2048, 2048), dtype=np.float32)
    logfile.write("starting model "+m+'\n')
    for i in files:
        logfile.write("at this point, the running total has size: " + str(sys.getsizeof(total))+"\n")
        logfile.write("now starting to add to running total:\n")
        f = hp.File(BASE+i,'r')
        logfile.write("the hdf5 file that got opened has size " + str(sys.getsizeof(f))+"\n")
        logfile.write("size of the array being added: "+ str(sys.getsizeof(f[m][:]))+"\n")
        total += f[m][:]
        logfile.write("after adding, the running total has size: " + str(sys.getsizeof(total))+"\n")
        f.close()
    w.create_dataset(m, data=total, compression="gzip", compression_opts=9)
w.close()
logfile.close()
