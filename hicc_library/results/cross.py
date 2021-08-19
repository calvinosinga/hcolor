"""
"""
import h5py as hp
import numpy as np
import time
import matplotlib.pyplot as plt
from Pk_library import XPk, XXi

class Cross():
    def __init__(self, gridfilepath1, gridfilepath2, outfilepath,
            plotpath):
        
        self.g1 = hp.File(gridfilepath1, 'r')
        self.g2 = hp.File(gridfilepath2,'r')
        self.outfile = hp.File(outfilepath, 'w')
        self.plotpath = plotpath

        self.saved_k = False
        self.saved_k2D = False
        self.saved_r = False
        return

    def computeResults(self):
        g1names = list(self.g1.keys())
        g2names = list(self.g2.keys())
        for i in range(len(g1names)):
            for j in range(len(g2names)):
                dat1 = self.g1[g1names[i]]
                dat2 = self.g2[g2names[j]]
                dct1 = dict(dat1.attrs)
                dct2 = dict(dat2.attrs)
                if not (dct1['ignore'] or dct2['ignore']):
                    if dct1["in_rss"] == dct2["in_rss"]:
                        gridname1 = dct1['gridname']
                        gridname2 = dct2['gridname']
                        keyname = "%sX%s"%(gridname1, gridname2)
                        dat1 = self._toOverdensity(dat1[:], dct1)
                        dat2 = self._toOverdensity(dat2[:], dct2)
                        self._computeXpk([dat1,dat2],dct1, keyname+'_pk')
                        self._computeXxi([dat1,dat2],dct1, keyname+'_xi')
        
        self.outfile.close()
        self.g1.close()
        self.g2.close()
        return
                    
    def _computeXpk(self, grids, dct, name):
        xpk = XPk(grids, dct['BoxSize'], dct['axis'], MAS=['CIC','CIC'])
        if not self.saved_k:
            self.saved_k = True
            self.outfile.create_dataset('k', data=xpk.k3D)
        self.outfile.create_dataset(name, data=xpk.XPk[:,0,0])
        if dct['in_rss']:
            self.outfile.create_dataset(name+'2D', data=xpk.PkX2D[:,0])
            if not self.saved_k2D:
                self.outfile.create_dataset("kper", data=xpk.kper)
                self.outfile.create_dataset("kpar", data=xpk.kpar)
                self.saved_k2D = True
        
            
        return
        
    def _computeXxi(self, grids, dct, name):
        xxi = XXi(grids[0], grids[1], dct['BoxSize'], axis = dct['axis'], MAS=('CIC','CIC'))

        self.outfile.create_dataset(name, data=xxi.xi[:,0])
        if not self.saved_r:
            self.outfile.create_dataset('r', data=xxi.r3D)
        
        return
        
    def _toOverdensity(self, grid, dct):
        grid = grid/dct["BoxSize"]**3
        grid = grid/np.mean(grid).astype(np.float32)
        grid = grid - 1    
        return grid