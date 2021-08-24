import numpy as np
import h5py as hp
import illustris_python as il
import os

class Field():
    def __init__(self, fieldname, simname, snapshot, axis, 
                resolution, verbose):
        self.simname = simname
        self.snapshot = snapshot
        self.resolution = resolution
        self.axis = axis
        self.fieldname = fieldname

        self.v = verbose

        if self.v:
            print("\n\ninputs given to superclass constructor:")
            print("the simulation name: %s"%self.simname)
            print("the snapshot: %d"%self.snapshot)
            print("the axis: %d"%self.axis)
            print("the resolution: %d"%self.resolution)
        
        # given values later, stated here so I know they exist
        self.hasAuto = {}
        self.hasGrid = {}
        
        self.isPtl = False
        self.combinedChunks = []
        
        # to be implemented in subclasses
        self.gridfile = ''
        self.gridnames = []
        self.ignore = []
        self.isHI = True
        return

    def loadSimHeader(self, snapfilepath):
        f = hp.File(snapfilepath, 'r')
        head = dict(f['Header'].attrs)
        temp = dict(f['Parameters'].attrs)
        params = ['HubbleParam']
        for p in params:
            head[p] = temp[p]
        
        # boxsize given in ckpc/h
        head['BoxSize'] *= head['Time'] / head['HubbleParam']

        # Masstable given in 1e10 Msun/h
        head['MassTable'] *= 1e10 / head['HubbleParam']
        if self.v:
            print("simulation header loaded:")
            print(self.header)
        
        self.header = head
        return
    
    
    def computePk(self):
        return
    
    def computeXi(self):
        return
    
    def makeSlice(self):
        return

    def computeGrids(self):
        return
    
    def shiftToRedshiftSpace(self, pos = None, vel = None):
        if pos is None:
            pos = self.pos
        if vel is None:
            vel = self.vel
        
        boxsize = self.header["BoxSize"]
        hubble = self.header["HubbleParam"] * 100
        redshift = self.header['Redshift']

        factor = (1 + redshift) / hubble
        pos[:, self.axis] += vel[:, self.axis] * factor

        # handle periodic boundary conditions
        pos[:, self.axis] = np.where((pos[:,self.axis]>boxsize) | (pos[:,self.axis]<0), 
                (pos[:,self.axis]+boxsize)%boxsize, pos[:,self.axis])
        return pos
    
    def loadGroupcat(self, simpath, fields):
        return il.groupcat.loadSubhalos(simpath,
                self.snapshot, fields=fields)
    
    def setPaths(self, gd):
        self.gridpath = gd['grids']
        return

    # helper methods

    def _makeHasAutoDict(self):
        for g in self.gridnames:
            self.hasAuto[g] = False
        return
    
    def _makeHasGridDict(self):
        for g in self.gridnames:
            self.hasGrid[g] = False
        return


        
    