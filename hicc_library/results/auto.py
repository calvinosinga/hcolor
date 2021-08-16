import h5py as hp
import time
import numpy as np
import matplotlib.pyplot as plt
from Pk_library import Pk, Xi
import matplotlib as mpl
import copy

class Auto():
    def __init__(self, gridfilepath, outfilepath, plotpath):

        self.gridfile = hp.File(gridfilepath, 'r')
        self.outfile = hp.File(outfilepath, 'w')
        self.plotpath = plotpath

        self.saved_k = False
        self.saved_k2D = False
        self.saved_r = False
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
                self._makeSlice(grid, dct, g+"_slc")
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
        if not self.saved_r:
            self.outfile.create_dataset("r", data=xi.r3D)
            self.saved_r = True
        self.outfile.create_dataset(savename, data=xi.xi[:,0])
        return
    
    def _makeSlice(self, grid, dct, savename, perc=0.1, mid=None):
        cmap = copy.copy(mpl.cm.get_cmap("plasma"))
        # cmap.set_under('w')
        dim = grid.shape[0]
        slcidx = int(perc*dim) # the percentage of the volume that should be binned
        if mid is None:
            mid = int(dim/2)
        slc = np.log10(np.sum(grid[:, mid-slcidx:mid+slcidx, :], axis=1))
        self.outfile.create_dataset(savename, data=slc)
        plt.imshow(slc, extent=(0, dct['BoxSize'], 0, dct['BoxSize']), origin='lower', cmap=cmap)
        plt.xlabel("x (Mpc/h)")
        plt.ylabel("y (Mpc/h)")
        cbar = plt.colorbar()
        cbar.set_label("Mass (Solar Masses)")
        plt.savefig(self.plotpath+savename+".png")
        plt.clf()
        return
    
