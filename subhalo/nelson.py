"""
Subhalo Run except I'm using Mpc/h and solar masses as my units.
"""
import numpy as np
import h5py as hp
import sys

########## INPUTS #################
grid = (2048,2048,2048)
FILENO = int(sys.argv[1])
SNAPSHOT = sys.argv[2]
RUN = sys.argv[3]
h=0.6774
BOXSIZE = 75.0 #kpc/h
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
    return stmass > refmass and gasmass > refmass

###################################
logfile = open(SAVE+'nelson_'+RUN+'_log'+str(SNAPSHOT)+'.txt', 'a')
logfile.write('the refmass is: %.4E\n'%(200*MEANBARYONICMASS))
redfield = np.zeros(grid, dtype=np.float32)
bluefield = np.zeros(grid, dtype=np.float32)
nondetfield = np.zeros(grid, dtype=np.float32)
counts = np.zeros(3)
edges = np.linspace(0,BOXSIZE, grid[0]-1) #definitions of bins
w = hp.File(SAVE+'nelson_'+RUN+'_'+str(SNAPSHOT)+'.final.hdf5', 'w')
for i in range(FILENO):
    try:
        f = hp.File(HOME+'fof_subhalo_tab_0'+str(SNAPSHOT)+'.'+str(i)+'.hdf5','r')
    except IOError:
        logfile.write('failed to open file for '+str(i)+'\n')
    else:
        try:
            pos = f['Subhalo']['SubhaloCM']/1e3 #Mpc/h
            mass = f['Subhalo']['SubhaloMassType']*1e10/h #solar masses
            photo = f['Subhalo']['SubhaloStellarPhotometrics']
        except:
            logfile.write("chunk "+str(i)+ '\'s subhalo data was empty\n')
        else:
            bins = np.digitize(pos,edges)
            for j,b in enumerate(bins):
                gr = photo[j][4]-photo[j][5]
                if is_resolved(mass[j][4], mass[j][0]) and isred(gr,mass[j][4]):
                    redfield[b[0],b[1],b[2]]+= np.sum(mass[j])
                    counts[2]+=1
                if is_resolved(mass[j][4], mass[j][0]) and not isred(gr,mass[j][4]):
                    bluefield[b[0],b[1],b[2]]+= np.sum(mass[j])
                    counts[0]+=1
                if not is_resolved(mass[j][4], mass[j][0]):
                    nondetfield[b[0],b[1],b[2]]+= np.sum(mass[j])
                    counts[1]+=1

w.create_dataset("red",data=redfield, compression="gzip", compression_opts=9)
w.create_dataset("blue",data=bluefield, compression="gzip", compression_opts=9)
w.create_dataset("nondetection",data=nondetfield, compression="gzip", compression_opts=9)
w.create_dataset('counts',data=counts, compression="gzip", compression_opts=9)
w.close()
