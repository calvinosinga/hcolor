import matplotlib.pyplot as plt
import h5py as hp
import numpy as np

f = hp.File("/lustre/diemer/illustris/hih2/hih2_particles_099.4.hdf5",'r')
f_neut_h = f['PartType0']['f_neutral_H'][:]
print(np.min(f_neut_h), np.max(f_neut_h))
hist=plt.hist(f_neut_h)
print(hist[0])
plt.savefig("/lustre/cosinga/hiptl_output/neutral_fraction_histogram.4.png")
plt.clf()
f_mol = f['PartType0']['f_mol_GD14'][:]
print(np.min(f_mol), np.max(f_mol))
hist=plt.hist(f_mol)
print(hist[0])
plt.savefig("/lustre/cosinga/hiptl_output/f_mol_GD14.4.png")
