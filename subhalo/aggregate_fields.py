"""
Makes the total subhalo fields and the detection fields, for each Nelson run
"""
import h5py as hp
import numpy as np
BASE = '/lustre/cosinga/final_fields/'
grid = (2048, 2048, 2048)
def agg(filename):

    s = hp.File(BASE+filename,'a')
    field = np.zeros(grid, dtype=np.float32)
    field += s['red'][:]
    field += s['blue'][:]
    s.create_dataset("detection", data=field, compression="gzip", compression_opts=9)
    field += s['nondetection'][:]
    s.create_dataset("total", data=field, compression="gzip", compression_opts = 9)
    s.close()

agg("nelson_high_99.final.hdf5")
agg("nelson_low_99.final.hdf5")
agg("nelson_mid_99.final.hdf5")
