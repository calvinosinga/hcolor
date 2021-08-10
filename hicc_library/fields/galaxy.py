#!/usr/bin/env python3
"""

"""

from hicc_library.grid.grid import Grid
from hicc_library.fields.field_super import Field
import h5py as hp
import numpy as np

def isRed(gr, stmass):
    return

def isResolved(stmass):
    return
class galaxy(Field):

    def __init__(self, paths, simname, snapshot, resolution, outfile):
        super().__init__(paths, simname, snapshot, resolution, outfile)

        self.gridnames = ['blue','red','unresolved', 'all']

        fields = ['SubhaloStellarPhotometrics','SubhaloPos','SubhaloMassType',
                'SubhaloVel']
        
        data = self._loadGalaxyData(fields)
        self.pos = data['SubhaloPos'][:]
        self.vel = data['SubhaloVel'][:]
        self.gr = data['SubhaloStellarPhotometrics'][:,4] - \
                data['SubhaloStellarPhotometrics'][:,5]
        self.mass = data['SubhaloMassType'][:]

        self._convertMass()
        self._convertPos()
        self._convertVel()

        # whenever we want to compute galaxy grids, we also want a corresponding
        # color-stmass plot
        self.plotColorStellar()
        return
    
    def computeGrids(self):
        blue_mask = 
        for g in self.gridnames:
            self._computeHI(g)
        
        self._toRedshiftSpace()
        for g in self.gridnames:
            self._computeHI(g+'rs')
        self.gridsave.close()
        return
    

    def makeColorStellar(self):
        # make a color-stmass plot

        # save 
        return
