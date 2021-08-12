"""
This file is responsible for the creation of the contituent sbatch files that make
up the pipeline.
"""
import os
import illustris_python as il
import numpy as np
import h5py as hp

class Field():

    def __init__(self, gd, simname, snapshot, axis, resolution, outfilepath):
        self.simname = simname
        self.snapshot = snapshot
        self.resolution = resolution
        self.axis = axis
        self.gd = gd
        self.v = gd['verbose']
        self.outfile = hp.File(outfilepath, 'w')

        if self.v:
            print("\n\ninputs given to superclass constructor:")
            print("the simulation name: %s"%self.simname)
            print("the snapshot: %d"%self.snapshot)
            print("the axis: %d"%self.axis)
            print("the resolution: %d"%self.resolution)
            print("saving to filepath %s"%outfilepath)
        
        self.in_rss = False #used to tell grids if the positions are redshifted or not
        


        # getting basic simulation information
        
        f = hp.File(gd['load_header'], 'r')
        self.header = dict(f['Header'].attrs)
        temp = dict(f['Parameters'].attrs)
        paramparams = ['BoxSize', 'HubbleParam']
        for p in paramparams:
            self.header[p] = temp[p]
        self.header['BoxSize'] = self._convertPos(self.header['BoxSize'])
        self.header['MassTable'] = self._convertMass(self.header['MassTable'])

        # other variables expected to be assigned values later in analysis
        self.grid = None
        self.fieldname = ''
        self.pos = None
        self.vel = None
        self.mass = None
        self.gridnames = []
        return
    
    def computeGrids(self):
        pass
    
    def saveData(self):
        # saves grid. resolution, rss (combine info if chunk) -> attrs
        dat = self.grid.saveGrid(self.outfile)
        dct = dict(dat.attrs)
        dct['simname'] = self.simname
        dct['snapshot'] = self.snapshot
        dct['axis'] = self.axis
        return dat
    
    def _loadSnapshotData(self):
        """
        The fields that use snapshot data vary in what they need too much,
        so the implementation is left to the subclasses.
        """
        pass
    
    def _loadGalaxyData(self, fields):
        return il.groupcat.loadSubhalos(self.gd[self.simname],
                self.snapshot, fields=fields)
    
    def _toRedshiftSpace(self):
        if self.pos is None or self.vel is None:
            raise ValueError("position or velocity have not been defined yet")
        if self.in_rss:
            raise ValueError("already in redshift-space!")
        boxsize = self._convertPos(self.header["BoxSize"])
        hubble = self.header["HubbleParam"]*100 # defined using big H
        redshift = self.header['Redshift']

        factor = (1+redshift)/hubble
        self.pos[:,self.axis] += self.vel[:,self.axis]*factor

        # handle periodic boundary conditions
        self.pos[:, self.axis] = np.where((self.pos[:,self.axis]>boxsize) | (self.pos[:,self.axis]<0), 
                (self.pos[:,self.axis]+boxsize)%boxsize, self.pos[:,self.axis])
        
        self.in_rss = True
        return

    def _convertMass(self, mass=None):
        """
        Converts mass units from 1e10 M_sun/h to M_sun
        """
        if mass is None:
            self.mass *= 1e10/self.header['HubbleParam']
            return
        else:
            mass *= 1e10/self.header['HubbleParam']
            return mass
    
    def _convertPos(self, pos=None):
        """
        Converts position units from ckpc/h to Mpc
        """
        if pos is None:
            self.pos *= self.header["Time"]/1e3
            return
        else:
            pos *= self.header["Time"]/1e3
            return pos
    
    def _convertVel(self, vel=None):
        """
        Multiplies velocities by scale factor^0.5
        """
        if vel is None:
            self.vel *= np.sqrt(self.header["Time"])
            return
        else:
            vel *= np.sqrt(self.header["Time"])
            return vel
    

