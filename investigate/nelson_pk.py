"""
This is investigating the strange sinusoidal pattern in the power
by creating plots of slices of the blue nelson field.
"""
import matplotlib.pyplot as plt
import matplotlib.colors as mpc
import h5py as hp
import numpy as np
import sys
idx = int(sys.argv[1])

f = hp.File("/lustre/cosinga/final_fields/nelson_99.final.hdf5", 'r')
for k in ('blue', 'red', 'total'):
    slc = f[k][idx-100:idx+100,:,:]
    print(slc.shape)
    slc = np.sum(slc, axis=0)
    print(slc.shape)
    slc /= 200
    #plt.imshow(slc)
    #levs = [0,0.01,0.05,0.1,0.5,1,5,10]
    #cols = ['white','lightcyan','lightblue','deepskyblue','dodgerblue','royalblue','mediumblue','midnightblue']
    #plt.contourf(slc, levels=levs, colors=cols)
    plt.contourf(slc, norm = mpc.LogNorm())
    plt.colorbar()
    plt.title(k+' Subhaloes '+str(np.count_nonzero(slc)))
    plt.savefig("/lustre/cosinga/final_fields/slices/"+k+"_slice%d.png"%idx)
    plt.clf()
    slc = slc[0::2,:]+slc[1::2,:]
    print(slc.shape)
    slc = slc[:,0::2]+slc[:,1::2]
    print(slc.shape)
    slc /= 4
    #plt.contourf(slc, levels=levs, colors=cols)
    plt.contourf(slc, norm = mpc.LogNorm())
    plt.colorbar()
    plt.title(k+' Subhaloes Pixelized ' + str(np.count_nonzero(slc)))
    plt.savefig("/lustre/cosinga/final_fields/slices/"+k+"_slicepix%d.png"%idx)
    plt.clf()




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
