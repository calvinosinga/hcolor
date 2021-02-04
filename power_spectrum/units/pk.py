from Pk_library import Pk
import sys
import numpy as np
import h5py as hp

HOME='/lustre/cosinga/final_fields/'
filename = sys.argv[1]
savename = sys.argv[2]

print('the filename is: ' + filename)
BOXSIZE = 75000.0 #kpc/h
grid = (2048, 2048, 2048)
f = hp.File(HOME+filename, 'r')
keys = list(f.keys())
print('the keys of the field are: '+str(keys))
for k in keys:
    field = f[k][:]
    print("the shape of the field is: " + str(field.shape))
    if field.shape == grid:
        field = field/(BOXSIZE**3) #converts to a density
        avg = np.mean(field).astype(np.float32)
        field = field/avg; field = field - 1
        pk = Pk(field, BOXSIZE, axis=0, MAS='NGP')
        tpk = np.transpose([pk.k3D, pk.Pk[:,0]])
        np.savetxt(HOME+'pk/'+savename+'_'+k+".txt", tpk)
f.close()
