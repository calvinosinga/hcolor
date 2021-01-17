"""
This is investigating the strange sinusoidal pattern in the power
by creating plots of slices of the 
"""
import matplotlib.pyplot as plt
import h5py as hp
import numpy as np

f = hp.File("/lustre/cosinga/final_fields/nelson_99.final.hdf5", 'r')
slc = f['blue'][1000,:,:]
grid = (2048,2048,2048)
plt.imshow(np.log10(slc))
plt.colorbar()
plt.title(str(np.sum(slc))+' '+str(np.min(slc))+' '+str(np.max(slc)))
plt.savefig("/lustre/cosinga/final_fields/slices/blue_slice1000.png")

