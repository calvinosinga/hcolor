import numpy as np
import h5py as hp
import sys
import MAS_library as masl
import redshift_space_library as rsl
########## INPUTS #################
grid = (2048,2048,2048)
FILENO = int(sys.argv[1])
SNAPSHOT = sys.argv[2]
RUN = sys.argv[3]
AXIS = float(sys.argv[4])
MAS = sys.argv[5]
h=0.6774
BOXSIZE = 75.0 #Mpc/h
HOME = '/lustre/cosinga/subhalo'+str(SNAPSHOT)+'/'
SAVE = '/lustre/cosinga/subhalo_output/'
MEANBARYONICMASS=1.4e6 #solar masses
# these values were taken from Pillepich 2018 -> average baryonic mass in table
# in another Pillepich paper from 2017 the median? gas cell mass from the graph appears ~2 x 10^6
def isred(gr, stmass):#color definition as given by Benedikt
    if RUN == 'high':
        return gr> 0.675 + 0.02*(np.log10(stmass)-10.28)
    elif RUN == 'low':
        return gr> 0.625 + 0.02*(np.log10(stmass)-10.28)
    elif RUN == 'mid':
        return gr> 0.65 + 0.02*(np.log10(stmass)-10.28)

def is_resolved(stmass, gasmass):
    """
    tests if the subhalo is well-resolved.
    """
    refmass = MEANBARYONICMASS*200
    resolved_in_stmass = stmass > refmass
    resolved_in_gasmass = gasmass > refmass
    return resolved_in_gasmass * resolved_in_stmass

###################################
logfile = open(SAVE+'nelson_'+RUN+'_log'+str(SNAPSHOT)+'.txt', 'w')
logfile.write('the refmass is: %.4E\n'%(200*MEANBARYONICMASS))
redfield = np.zeros(grid, dtype=np.float32)
bluefield = np.zeros(grid, dtype=np.float32)
nondetfield = np.zeros(grid, dtype=np.float32)
count = np.zeros(3)

w = hp.File(SAVE+'nelson_rs_'+RUN+'_'+str(AXIS)+'_'+str(SNAPSHOT)+'.final.hdf5', 'w')
for i in range(FILENO):
    try:
        f = hp.File(HOME+'fof_subhalo_tab_0'+str(SNAPSHOT)+'.'+str(i)+'.hdf5','r')
    except IOError:
        logfile.write('failed to open file for '+str(i)+'\n')
    else:
        try:
            pos = f['Subhalo']['SubhaloCM'][:]/1e3 #Mpc/h
            mass = f['Subhalo']['SubhaloMassType'][:]*1e10/h #solar masses
            vel = f['Subhalo']['SubhaloVel'][:] # km/s
            photo = f['Subhalo']['SubhaloStellarPhotometrics'][:]
        except KeyError:
            logfile.write("chunk "+str(i)+ '\'s subhalo data was empty\n')
        else:
            #get needed constants
            cons = f['Header'].attrs
            redshift = cons[u'Redshift']
            omega_L = cons[u'OmegaLambda']
            omega_m = cons[u'Omega0']
            HUBBLE = 100.0*np.sqrt(omega_m*(1+redshift)**3+omega_L) #km/s/(Mpc/h)

            logfile.write("starting procedure for chunk %d"%i)

            # move to redshift space
            rsl.pos_redshift_space(pos,vel,BOXSIZE,HUBBLE, redshift, AXIS)

            gr = photo[:,4]-photo[:,5]
            total_mass = np.sum(mass,axis=1)
            stmass = mass[:,4]
            # now getting the indices of resolved subhaloes
            resolved_idx = is_resolved(stmass, mass[:,0])

            # now creating field for the nondetected subhaloes
            nondetection_idx = np.invert(resolved_idx)
            count[1] += np.sum(nondetection_idx) #adding to running nondet total
            masl.MA(pos[nondetection_idx], nondetfield, float(BOXSIZE), MAS, total_mass[nondetection_idx])

            # removing unresolved from pos/mass/gr/stmass
            total_mass = total_mass[resolved_idx]
            pos = pos[resolved_idx]
            gr = gr[resolved_idx]
            stmass = stmass[resolved_idx]

            # now creating field for the red subhaloes
            red_idx = isred(gr, stmass)
            count[2] += np.sum(red_idx)
            masl.MA(pos[red_idx], redfield, BOXSIZE, MAS, total_mass[red_idx])

            # now creating field for the blue subhaloes
            blue_idx = np.invert(red_idx)
            count[0] += np.sum(blue_idx)
            masl.MA(pos[blue_idx], bluefield, BOXSIZE, MAS, total_mass[blue_idx])

w.create_dataset("red",data=redfield, compression="gzip", compression_opts=9)
w.create_dataset("blue",data=bluefield, compression="gzip", compression_opts=9)
w.create_dataset("nondetection",data=nondetfield, compression="gzip", compression_opts=9)
w.create_dataset('counts',data=count, compression="gzip", compression_opts=9)
w.close()
