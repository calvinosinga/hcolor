import numpy as np
import h5py as hp
import sys
BASE = '/lustre/cosinga/hiptl_output/'
START = sys.argv[1]
END = sys.argv[2]
filenos = np.arange(int(START), int(END))
SNAPSHOT = sys.argv[3]
logfile = open(BASE+"combine_test_log.txt",'w')
w = hp.File(BASE+"hiptl_"+SNAPSHOT+'.'+START+'.'+END+'.hdf5','w')
models = ['GD14', 'GK11', 'K13', 'S14']
files = ['hiptl_'+str(SNAPSHOT)+'.'+str(i)+'.hdf5' for i in filenos]
logfile.write('first file: ' + files[0]+'\n')
logfile.write('last file: ' + files[-1]+'\n')
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
