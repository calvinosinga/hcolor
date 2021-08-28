"""
This file is responsible for the creation of the contituent sbatch files that make
up the pipeline.
"""
import os
import illustris_python as il
import numpy as np
import h5py as hp
import matplotlib.pyplot as plt
from Pk_library import Pk, Xi, XPk, XXi
import matplotlib as mpl
import copy

class Field():

    def __init__(self, simname, snapshot, axis, resolution, pkl_path, verbose):
        # getting default class variables
        self.simname = simname
        self.snapshot = snapshot
        self.resolution = resolution
        self.axis = axis
        self.pkl_path = pkl_path
        self.v = verbose

        # class variables for results
        self.saved_k = False
        self.saved_k2D = False
        self.saved_r = False


        self.pks = {}
        self.xi = {}
        self.slices = {}
        self.tdpks = {}

        if self.v:
            print("\n\ninputs given to superclass constructor:")
            print("the simulation name: %s"%self.simname)
            print("the snapshot: %d"%self.snapshot)
            print("the axis: %d"%self.axis)
            print("the resolution: %d"%self.resolution)
        
        self.header = None # dictionary that stores basic sim info
        


        # other variables expected to be assigned values in subclasses
        self.fieldname = ''
        self.gridnames = []
        self.isHI = True
        return
    
    def loadHeader(self, snappath):
        f = hp.File(snappath, 'r')
        self.header = dict(f['Header'].attrs)
        temp = dict(f['Parameters'].attrs)
        paramparams = ['BoxSize', 'HubbleParam']
        for p in paramparams:
            self.header[p] = temp[p]
        self.header['BoxSize'] = self._convertPos(self.header['BoxSize'])
        self.header['MassTable'] = self._convertMass(self.header['MassTable'])
        return
    
    def computeGrids(self, outfile):
        if self.header is None:
            raise ValueError("header needs to be loaded before computing grids")
        dat = outfile.create_dataset('pickle', data=[0])
        dat.attrs['path'] = self.pkl_path
        return
    
    def computeAux(self):
        """
        Compute auxiliary information/plots
        """
        return
    
    def computePk(self, grid):
        arr = grid.getGrid()
        arr = self._toOverdensity(arr)
        pk = Pk(arr, self.header["BoxSize"], axis = self.axis, MAS='CIC')
        if not self.saved_k:
            self.pks['k'] = pk.k3D
            self.saved_k = True
        self.pks[grid.gridname] = pk.Pk[:,0]

        if grid.in_rss:
            if not self.saved_k2D:
                self.tdpks['kper'] = pk.kper
                self.tdpks['kpar'] = pk.kpar
            self.tdpks[grid.gridname] = pk.Pk[:,0]
        
        return
    
    def computeXi(self, grid):
        if not grid.ignore:
            arr = grid.getGrid()
            arr = self._toOverdensity(arr)
            xi = Xi(arr, self.header["BoxSize"], axis = self.axis, MAS='CIC')
            if not self.saved_r:
                self.xi["r"]=xi.r3D
                self.saved_r = True
            self.xi[grid.gridname] = xi.xi[:,0]
        return

    def makeSlice(self, grid, perc=0.1, mid=None):
        if not grid.ignore:
            # cmap.set_under('w')
            arr = grid.getGrid()
            dim = arr.shape[0]
            slcidx = int(perc*dim) # the percentage of the volume that should be binned
            if mid is None:
                mid = int(dim/2)
            slc = np.log10(np.sum(arr[:, mid-slcidx:mid+slcidx, :], axis=1))
            self.slices[grid.gridname] = slc
        return
    
    def saveData(self, outfile, grid):
        # saves grid. resolution, rss (combine info if chunk) -> attrs
        dat = grid.saveGrid(outfile)
        return dat
    
    def _loadSnapshotData(self):
        """
        The fields that use snapshot data vary in what they need too much,
        so the implementation is left to the subclasses. ptl, for example, needs
        data on all of the particles whereas hiptl just needs gas particles.
        Thus anything put here will necessarily be overwritten anyway in a subclass.
        """
        pass
    
    def _loadGalaxyData(self, simpath, fields):
        return il.groupcat.loadSubhalos(simpath, self.snapshot, fields=fields)
    
    def _toRedshiftSpace(self, pos, vel):
        boxsize = self.header["BoxSize"]
        hubble = self.header["HubbleParam"]*100 # defined using big H
        redshift = self.header['Redshift']

        factor = (1+redshift)/hubble
        pos[:,self.axis] += vel[:,self.axis]*factor

        # handle periodic boundary conditions
        pos[:, self.axis] = np.where((pos[:,self.axis]>boxsize) | (pos[:,self.axis]<0), 
                (pos[:,self.axis]+boxsize)%boxsize, pos[:,self.axis])
        
        return pos

    def _convertMass(self, mass):
        """
        Converts mass units from 1e10 M_sun/h to M_sun
        """
        mass *= 1e10/self.header['HubbleParam']
        return mass
    
    def _convertPos(self, pos=None):
        """
        Converts position units from ckpc/h to Mpc
        """
        pos *= self.header["Time"]/1e3
        return pos
    
    def _convertVel(self, vel=None):
        """
        Multiplies velocities by scale factor^0.5
        """
        vel *= np.sqrt(self.header["Time"])
        return vel
    
    def _toOverdensity(self, arr):
        arr = arr/self.header['BoxSize']**3
        arr = arr/np.mean(arr).astype(np.float32)
        arr = arr - 1

        return arr


from hicc_library.grid.grid import Grid
class Cross():
    def __init__(self, field1, field2, gridfilepath1, gridfilepath2):
        self.field1 = field1
        self.field2 = field2
        self.gfpath1 = gridfilepath1
        self.gfpath2 = gridfilepath2

        self.saved_xk = False
        self.saved_xr = False
        self.saved_xk2D = False
        self.xpks = {}
        self.xxis = {}
        self.tdxpks = {}

        self.box = self.field1.header['BoxSize']
        self.axis = self.field2.axis
        return
    
    def _loadHdf5(self):
        gf1 = hp.File(self.gfpath1, 'r')
        gf2 = hp.File(self.gfpath2, 'r')
        return gf1, gf2
    
    def computeXpks(self):
        gf1, gf2 = self._loadHdf5()
        keylist1 = self._getKeys(gf1)
        keylist2 = self._getKeys(gf2)
        for k1 in keylist1:
            for k2 in keylist2:
                grid1 = Grid.loadGrid(gf1[k1])
                grid2 = Grid.loadGrid(gf2[k2])
                self._xpk(grid1, grid2)
        return
    
    def _xpk(self, grid1, grid2):
        if not grid1.ignore and not grid2.ignore and grid1.in_rss == grid2.in_rss:
            kname = '%sX%s'%(grid1.gridname, grid2.gridname)
            arrs = (self._toOverdensity(grid1.getGrid()), 
                    self._toOverdensity(grid2.getGrid()))
            xpk = XPk(arrs, self.box, self.axis, MAS=['CIC','CIC'])
            if not self.saved_xk:
                self.addXpk('k',xpk.k3D)
                self.saved_xk = True
            self.addXpk(kname, xpk.Xpk[:,0,0])

            if grid1.in_rss and grid2.in_rss:
                if not self.saved_xk2D:
                    self.add2DXpk('kper', xpk.kper)
                    self.add2DXpk('kpar', xpk.kpar)
                    self.saved_xk2D = True
                self.add2DXpk(kname, xpk.PkX2D[:,0])

        return

    def _getKeys(self, gfile):
        klist = list(gfile.keys())
        klist.remove('pickle')
        return klist

    def computeXxis(self):
        gf1, gf2 = self._loadHdf5()
        keylist1 = self._getKeys(gf1)
        keylist2 = self._getKeys(gf2)
        for k1 in keylist1:
            for k2 in keylist2:
                grid1 = Grid.loadGrid(self.gf1[k1])
                grid2 = Grid.loadGrid(self.gf2[k2])
                self._xxi(grid1, grid2)
        return
    
    def _xxi(self, grid1, grid2):
        if not grid1.ignore and not grid2.ignore and grid1.in_rss == grid2.in_rss:
            kname = '%sX%s'%(grid1.gridname, grid2.gridname)
            arrs = (self._toOverdensity(grid1.getGrid()), 
                    self._toOverdensity(grid2.getGrid()))
            xxi = XXi(arrs[0], arrs[1], self.box, self.axis, MAS=['CIC','CIC'])
            if not self.saved_xr:
                self.addXpk('r',xxi.r3D)
                self.saved_xr = True
            self.addXxi(kname, xxi.xi[:,0])

        return

    def addXpk(self, name, array):
        self.xpks[name] = array
        return
    
    def add2DXpk(self, name, array):
        self.tdxpks[name] = array
        return
    
    def addXxi(self, name, array):
        self.xxis[name] = array
        return
    
    def _toOverdensity(self, arr):
        arr = arr/self.box**3
        arr = arr/np.mean(arr).astype(np.float32)
        arr = arr - 1

        return arr
