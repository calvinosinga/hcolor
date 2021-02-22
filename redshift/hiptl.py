import numpy as np
import h5py as hp
import sys
import redshift_space_library as rsl
import MAS_library as masl

# inputs
CHUNK = sys.argv[1]
BASE = '/lustre/diemer/illustris/hih2/' 
HOME = '/lustre/cosinga/ptl99/'
SAVE = '/lustre/cosinga/hiptl_output/'
BOXSIZE = 75.0 #Mpc/h
h = .6774
grid = (2048,2048,2048)
models = ['GD14', 'GK11', 'K13', 'S14']
axes = (0,1,2)

# opening needed files, opening write file
w = hp.File(SAVE+'hiptl_rs_99.'+CHUNK+'.hdf5', 'w')
hih2file = hp.File(BASE+"hih2_particles_099."+CHUNK+".hdf5", 'r')
ptlfile = hp.File(HOME+"snap_099."+CHUNK+".hdf5", 'r')

# constants
redshift = ptlfile['Header'].attrs[u'Redshift']
scale_factor = ptlfile['Header'].attrs[u'Time']
omega_L = ptlfile['Header'].attrs[u'OmegaLambda']
omega_m = ptlfile['Header'].attrs[u'Omega0']
HUBBLE = 100.0*np.sqrt(omega_m*(1+redshift)**3+omega_L) #km/s/(Mpc/h)

# getting needed data
mass = ptlfile['PartType0']['Masses'][:]*1e10/h # solar masses
vel = ptlfile['PartType0/Velocities'][:]*np.sqrt(scale_factor) # km/s
pos = ptlfile['PartType0']['CenterOfMass'][:]/1e3 # ~150 MB
f_neut_h = hih2file['PartType0']['f_neutral_H'][:] #~100 MB


for a in axes:
    rsl.pos_redshift_space(pos, vel, BOXSIZE,HUBBLE, redshift,a)
    for m in models:
        field = np.zeros(grid, dtype=np.float32)
        h2_frac = hih2file['PartType0']['f_mol_'+m][:] # ~100 MB
        masshi = (1-h2_frac)*f_neut_h*mass # ~100 MB
        masshi = np.where(masshi >= 0, masshi, np.zeros(masshi.shape, dtype=np.float32))
        masshi = masshi.astype('float32')# decreases size by 50 MB
        masl.MA(pos,field,BOXSIZE,'CIC',masshi)
        w.create_dataset(m+'_%d'%a, data=field, compression="gzip", compression_opts=9)
w.close()
