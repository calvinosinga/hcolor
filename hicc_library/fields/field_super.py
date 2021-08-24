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
        self.v = gd['verbose']
        self.outfile = hp.File(outfilepath, 'w')
        self.simpath = gd[simname]
        if self.v:
            print("\n\ninputs given to superclass constructor:")
            print("the simulation name: %s"%self.simname)
            print("the snapshot: %d"%self.snapshot)
            print("the axis: %d"%self.axis)
            print("the resolution: %d"%self.resolution)
            print("saving to filepath %s"%outfilepath)
        
        self.in_rss = False 
        #used to tell grids if the positions are redshifted or not

        # getting basic simulation information
        
        f = hp.File(gd['load_header'], 'r')
        self.header = dict(f['Header'].attrs)
        temp = dict(f['Parameters'].attrs)
        paramparams = ['BoxSize', 'HubbleParam']
        for p in paramparams:
            self.header[p] = temp[p]
        self.header['BoxSize'] = self._convertPos(self.header['BoxSize'])
        self.header['MassTable'] = self._convertMass(self.header['MassTable'])

        # other variables expected to be assigned values in subclasses
        self.fieldname = ''
        self.gridnames = []
        return
    
    def computeGrids(self):
        return
    
    def computeAux(self):
        """
        Compute auxiliary information/plots
        """
        return
    
    def saveData(self, pickle_path):
        # saves grid. resolution, rss (combine info if chunk) -> attrs
        dat = self.grid.saveGrid(self.outfile)
        pickle_file = self.outfile.create_dataset('pickle')
        pickle_file.attrs['path'] = pickle_path
        return dat
    
    def _loadSnapshotData(self):
        """
        The fields that use snapshot data vary in what they need too much,
        so the implementation is left to the subclasses. ptl, for example, needs
        data on all of the particles whereas hiptl just needs gas particles.
        Thus anything put here will necessarily be overwritten anyway in a subclass.
        """
        pass
    
    def _loadGalaxyData(self, fields):
        return il.groupcat.loadSubhalos(self.simpath,
                self.snapshot, fields=fields)
    
    def _toRedshiftSpace(self, pos, vel):
        boxsize = self.header["BoxSize"]
        hubble = self.header["HubbleParam"]*100 # defined using big H
        redshift = self.header['Redshift']

        factor = (1+redshift)/hubble
        pos[:,self.axis] += vel[:,self.axis]*factor

        # handle periodic boundary conditions
        pos[:, self.axis] = np.where((pos[:,self.axis]>boxsize) | (pos[:,self.axis]<0), 
                (pos[:,self.axis]+boxsize)%boxsize, pos[:,self.axis])
        
        self.in_rss = True
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
    

