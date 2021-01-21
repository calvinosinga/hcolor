import numpy as np
import h5py as hp
import sys
BASE = '/lustre/cosinga/hiptl_output/'

logfile = open(BASE+"final_test_log.txt",'w')
w = hp.File(BASE+"hiptl_"+SNAPSHOT+'.final.hdf5','w')
models = ['GD14', 'GK11', 'K13', 'S14']
files = ['hiptl_99.200.448.hdf5', 'hiptl_99.0.100.hdf5','hiptl_99.100.200.hdf5']
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
