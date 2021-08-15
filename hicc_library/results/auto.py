import h5py as hp
import time
from h5py._hl import dataset
import numpy as np
from numpy.lib.npyio import save
from Pk_library import Pk, Xi

class Auto():
    def __init__(self, gridfilepath, outfilepath, plotpath):


        self.gridfile = hp.File(gridfilepath, 'r')
        self.outfile = hp.File(outfilepath, 'w')
        self.plotpath = plotpath

        self.saved_k = False
        self.saved_k2D = False
        self.saved_x = False
        return
    

    def computeResults(self):
        gridnames = list(self.gridfile.keys())
        for g in gridnames:
            grid = self.gridfile[g][:]
            dct = self.gridfile[g].attrs
            is_priority = dct["is_priority"]
            grid = self._toOverdensity(grid, dct)
            self._computePk(grid, dct, g+"_pk")
            if is_priority:
                self._computeXi(grid, dct, g+"_xi")
                self._plotSlice(grid, dct)
        return
    
    def _toOverdensity(self, grid, dct):
        grid = grid/dct["BoxSize"]**3
        grid = grid/np.mean(grid).astype(np.float32)
        grid = grid - 1    
        return grid
    
    def _computePk(self, grid, dct, savename):
        pk = Pk(grid[:], dct["BoxSize"], axis = dct["axis"], MAS='CIC')
        if not self.saved_k:
            self.outfile.create_dataset("k", data = pk.k3D)
            self.saved_k = True
        self.outfile.create_dataset(savename, data = pk.Pk[:,0])
        
        # save attributes
        if dct["is_rss"]:
            self.outfile.create_dataset(savename+"_2D", data=pk.Pk2D[:])
            if not self.saved_k2D:
                self.outfile.create_dataset("kper", data=pk.kper)
                self.outfile.create_dataset("kpar", data=pk.kpar)
                self.saved_k2D = True
        
        return

    def _computeXi(self, grid, dct, savename):
        xi = Xi(grid[:], dct["BoxSize"], axis = dct["axis"], MAS='CIC')
        if not self.saved_x:
            self.outfile.create_dataset("")
        return
    
    def _plotSlice(self):
        return
    
