import numpy as np
import h5py as hp
import sys

f = hp.File('/lustre/cosinga/final_fields/nelson_mid_99.final.hdf5','r')
for i in ('blue','red','nondetection'):
    print(np.isnan(f[i]).any())

