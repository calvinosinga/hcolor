import numpy as np
import h5py as hp
import sys
BASE = '/lustre/cosinga/hiptl_output/'
PREFIX = sys.argv[1]
SNAPSHOT = str(sys.argv[2])
logfile = open(BASE+"final_test_log.txt",'w')
w = hp.File(BASE+"hiptl_99.final.hdf5",'w')
models = ['GD14', 'GK11', 'K13', 'S14']
files = ['.300.448.hdf5', '.0.100.hdf5','.100.200.hdf5', '.200.300.hdf5']
files = [PREFIX+SNAPSHOT+f for f in files]
for m in models:
    total = np.zeros((2048, 2048, 2048), dtype=np.float32)
    logfile.write("starting model "+m+'\n')
    logfile.write("current total sum %.4f"%(np.sum(total)))
    for i in files:
        f = hp.File(BASE+i,'r')
        total += f[m][:]
        logfile.write("new sum:" + str(np.sum(total))+"\n")
        f.close()
    w.create_dataset(m, data=total, compression="gzip", compression_opts=9)
w.close()
logfile.close()
