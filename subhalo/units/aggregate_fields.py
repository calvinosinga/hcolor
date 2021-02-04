"""
Makes the total subhalo fields and the detection fields, for both the Nelson
and Swanson runs.
"""
import h5py as hp
import numpy as np
BASE = '/lustre/cosinga/final_fields/'
grid = (2048, 2048, 2048)
s = hp.File(BASE+"nelson_high_99.final.hdf5",'a')
field = np.zeros(grid, dtype=np.float32)
field += s['red'][:]
field += s['blue'][:]
s.create_dataset("detection", data=field, compression="gzip", compression_opts=9)
field += s['nondetection'][:]
s.create_dataset("total", data=field, compression="gzip", compression_opts = 9)
field = np.zeros(grid, dtype=np.float32)
n = hp.File(BASE+"nelson_low_99.final.hdf5",'a')

field += n['blue'][:]
field += n['red'][:]
n.create_dataset("detection", data=field, compression="gzip", compression_opts=9)
field += n['nondetection'][:]
n.create_dataset("total", data=field, compression="gzip", compression_opts = 9)
s.close()
n.close()
