import numpy as np
import h5py as hp
import sys
import redshift_space_library as rsl
import MAS_library as masl

########## INPUTS #################
grid = (2048,2048,2048)
SNAPSHOT = sys.argv[1]
BOXSIZE = 75 #Mpc/h
HOME = '/lustre/cosinga/subhalo'+str(SNAPSHOT)+'/'
SAVE = '/lustre/cosinga/subhalo_output/'

###################################
logfile = open(SAVE+'hisubhalo_rs_log'+str(SNAPSHOT)+'.txt', 'w')
w = hp.File(SAVE+'hisubhalo_rs_'+str(SNAPSHOT)+'.final.hdf5', 'w')
f = hp.File(HOME+'hih2_galaxy_0'+str(SNAPSHOT)+'.hdf5','r')
headfile = hp.File(HOME+'fof_subhalo_tab_099.0.hdf5', 'r')
idfile = hp.File(HOME+"id_pos"+str(SNAPSHOT)+".hdf5",'r')
velfile = hp.File(HOME+"id_vel"+str(SNAPSHOT)+'.hdf5','r')
cons = [headfile['Header'].attrs[u'Redshift'], headfile['Header'].attrs[u'Omega0'], headfile['Header'].attrs[u'OmegaLambda']]
HUBBLE = 100*np.sqrt(cons[1]*(1+cons[0])**3+cons[2]) #km/s/(Mpc/h)
pos = idfile['coordinates'][:]/1e3 #Mpc/h
vel = velfile['velocities'][:] #km/s -> already peculiar velocity

keys = list(f.keys())
models = []
for k in keys:
    if 'm_hi' in k:
        models.append(k)
logfile.write("the models used are: "+str(models)+'\n')
axes = (0,1,2)
for a in axes:
    check = (type(BOXSIZE), type(cons[0]), type(a), type(pos[0,0]), type(vel[0,0]))
    for c in check:
        logfile.write(str(c)+'\n')
    rsl.pos_redshift_space(pos.astype('float32'), vel.astype('float32'), float(BOXSIZE),float(HUBBLE), float(cons[0]),float(a))
    for m in models:
        field = np.zeros(grid, dtype=np.float32)
        mass = f[m][:]
        masl.MA(pos.astype(np.float32), field, float(BOXSIZE), 'CIC', mass.astype(np.float32)
        w.create_dataset(m+'_%d'%a, data=field, compression="gzip", compression_opts=9)

w.close()
