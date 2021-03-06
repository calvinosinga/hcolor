from Pk_library import XPk
import sys
import numpy as np
import h5py as hp

HOME='/lustre/cosinga/final_fields/'
firstfile = sys.argv[1]
firstfield = sys.argv[2]
secondfile = sys.argv[3]
secondfield = sys.argv[4]
savename = sys.argv[5]
BOXSIZE = 75.0 #Mpc/h
grid = (2048, 2048, 2048)
print('opening files')
f = hp.File(HOME+firstfile, 'r')
g = hp.File(HOME+secondfile, 'r')
if firstfield == 'ALL':
    ffields = list(f.keys())
else:
    ffields = [firstfield]
if secondfield == 'ALL':
    gfields = list(g.keys())
else:
    gfields = [secondfield]
print('starting loop')
for i in ffields:
    for j in gfields:
        if f[i].shape == grid and g[j].shape == grid:
            fgrid = f[i][:]/BOXSIZE**3
            ggrid = g[j][:]/BOXSIZE**3
            print('turned fields into densities')
            fgrid = fgrid/np.mean(fgrid); fgrid = fgrid - 1
            ggrid = ggrid/np.mean(ggrid); ggrid = ggrid - 1
            print('turned fields into overdensities')
            res = XPk([fgrid, ggrid], BOXSIZE, axis = 0, MAS=['CIC', 'CIC'])
            xpk = np.transpose([res.k3D, res.XPk[:,0,0]])
            np.savetxt(HOME+'pk/'+savename+'_'+i+'-'+j+'.txt', xpk)
