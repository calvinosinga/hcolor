import pickle as pkl
import numpy as np
from hicc_library.plots import figures as hfig

def smoothPk(k, pk, nmodes, nbins = 2):
    newk = np.zeros(k.shape[0]/nbins)
    newnm = np.zeros(nmodes.shape[0]/nbins)
    newpk = np.zeros(pk.shape[0]/nbins)

    for i in range(len(newk)):
        slc = slice(i*nbins, (i+1)*nbins)
        newk[i] = np.sum(k[slc] * nmodes[slc]) / np.sum(nmodes[slc])
        newnm[i] = np.sum(nmodes[slc])
        newpk[i] = np.sum(pk[slc] * nmodes[slc]) / np.sum(nmodes[slc])
    return newk, newpk, newnm


    
        
