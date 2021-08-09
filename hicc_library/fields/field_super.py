"""
This file is responsible for the creation of the contituent sbatch files that make
up the pipeline.
"""
import os
import numpy as np
import h5py as hp

class Field():

    def __init__(self, paths, simname, snapshot, axis, resolution, outfile):
        self.simname = simname
        self.snapshot = snapshot
        self.resolution = resolution
        self.axis = axis

        # expected to be given in subclasses
        self.gridnames = []
        self.gridsave = hp.File(outfile+'.hdf5', 'w')


        # getting basic simulation information
        
        f = hp.File(paths['load_header'], 'r')
        self.header = dict(f['Header'].attrs)
        self.header = dict(f['Header'].attrs)
        temp = dict(f['Parameters'].attrs)
        paramparams = ['BoxSize', 'HubbleParam']
        for p in paramparams:
            self.header[p] = temp[p]
        self.header['BoxSize'] = self._convertPos(self.header['BoxSize'])
        self.header['MassTable'] = self._convertMass(self.header['MassTable'])

        # other variables expected to be assigned values later in analysis
        self.grid = None
        self.pos = None
        self.vel = None
        self.mass = None
        return
    
    def computeGrids(self):
        pass
    
    def _toRedshiftSpace(self):
        if self.pos is None or self.vel is None:
            raise ValueError("position or velocity have not been defined yet")
        boxsize = self._convertPos(self.header["BoxSize"])
        hubble = self.header["HubbleParam"]*100 # defined using big H
        redshift = self.header['Redshift']

        factor = (1+redshift)/hubble
        self.pos[:,self.axis] += self.vel[:,self.axis]*factor

        # handle periodic boundary conditions
        self.pos[:, self.axis] = np.where((self.pos[:,self.axis]>boxsize) | (self.pos[:,self.axis]<0), 
                (self.pos[:,self.axis]+boxsize)%boxsize, self.pos[:,self.axis])
        
        # tell the Grid object that we've moved to redshift space
        self.grid.toRSS()
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
    

