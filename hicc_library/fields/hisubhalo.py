#!/usr/bin/env python3
"""

"""

from hicc_library.grid.grid import Grid
from hicc_library.fields.field_super import Field
import h5py as hp
import numpy as np

class hisubhalo(Field):

    def __init__(self, paths, simname, snapshot, resolution, outfile):
        super().__init__(paths, simname, snapshot, resolution, outfile)

        # making a list of the grids to be created
        models = ['GD14','GK11','K13','S14']
        proj = ['map','vol']
        self.gridnames = []
        for m in models:
            for p in proj:
                self.gridnames.append('m_hi_%s_%s'%(m,p))
        self.gridnames.append('m_hi_L08_map')

        self.hih2file = hp.File(paths['post']+'hih2_galaxy_%03d.hdf5'%snapshot,'r')
        ids = self.hih2file['id_subhalo'][:] # used to idx into the subhalo catalog
        ids = ids.astype(np.int32)
        fields = ['SubhaloPos', 'SubhaloVel']

        data = self._loadGalaxyData(fields)
        self.pos = data['SubhaloPos'][ids]
        self.vel = data['SubhaloVel'][ids]

        self._convertPos()
        self._convertVel()
        return
    
    def computeGrids(self):
        for g in self.gridnames:
            self._computeHI(g)
        
        self._toRedshiftSpace()
        for g in self.gridnames:
            self._computeHI(g+'rs')
        self.gridsave.close()
        return
    
    def _computeHI(self, gridname):

        self.grid = Grid(gridname, self.resolution)
        self.grid.in_rss = self.in_rss
        self.mass = self.hih2file[gridname][:] #already in solar masses

        self.grid.CICW(self.pos, self.header['BoxSize'], self.mass)
        self.grid.saveGrid(self.gridsave)
        return
