"""
This is investigating the strange sinusoidal pattern in the power
by creating plots of slices of the blue nelson field.
"""
import matplotlib.pyplot as plt
import h5py as hp
import numpy as np
import sys
idx = int(sys.argv[1])

f = hp.File("/lustre/cosinga/final_fields/nelson_99.final.hdf5", 'r')
for k in ('blue', 'red', 'total')
    slc = f[k][idx-100:idx+100,:,:]
    print(slc.shape)
    slc = np.sum(slc, axis=0)
    print(slc.shape)

    plt.imshow(slc)
    plt.colorbar()
    plt.title(k+' Subhaloes')
    plt.savefig("/lustre/cosinga/final_fields/slices/"+k+"_slice%d.png"%idx)




# i=1000
# grid = (2048,2048,2048)
# #lth = grid[0]//4 
# slc = f['blue'][i,:,:]
# flt = np.matrix.flatten(slc)
# flt = np.ma.masked_equal(flt, 0.0, copy=False)
# plt.title(str(np.sum(flt))+' '+str(np.min(flt))+' '+str(np.max(flt)))

# binspace = np.logspace(-7, 3, 10)
# plt.hist(flt)
# plt.savefig("/lustre/cosinga/final_fields/slices/blue_slice_hist1000.png")
# plt.clf()


# field = f['blue'][:]
# print(np.count_nonzero(field))
