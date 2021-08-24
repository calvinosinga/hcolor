#!/usr/bin/env python3
"""

"""

from hicc_library.grid.grid import Grid
from hicc_library.fields.field_super import Field
import h5py as hp
import numpy as np

class hisubhalo(Field):

    def __init__(self, gd, simname, snapshot, axis, resolution, outfilepath):
        super().__init__(gd, simname, snapshot, axis, resolution, outfilepath)
        self.fieldname = 'hisubhalo'
        self.gridnames = self.getMolFracModelsGal()
 
        self.use_cicw = gd['%s_use_cicw'%self.fieldname]
        self.hih2file = hp.File(gd['post']+'hih2_galaxy_%03d.hdf5'%snapshot,'r')
        ids = self.hih2file['id_subhalo'][:] # used to idx into the subhalo catalog
        ids = ids.astype(np.int32)
        fields = ['SubhaloPos', 'SubhaloVel']

        data = self._loadGalaxyData(fields) # implemented in superclass
        self.pos = data['SubhaloPos'][ids]
        self.vel = data['SubhaloVel'][ids]

        self._convertPos()
        self._convertVel()
        return
    
    @staticmethod
    def getMolFracModelsGal():
        """
        Returns a list of the molecular fraction models provided by Diemer+ 2018,
        specifically the ones that correspond to the subhalo catalog.
        """
        models = ['GD14','GK11','K13','S14']
        proj = ['map','vol']
        gridnames = []
        for m in models:
            for p in proj:
                gridnames.append('m_hi_%s_%s'%(m,p))
        gridnames.append('m_hi_L08_map')
        return gridnames
    
    def computeGrids(self):
        for g in self.gridnames:
            self._computeHI(g)
        
        self._toRedshiftSpace()
        for g in self.gridnames:
            self._computeHI(g)
        
        self.outfile.close()
        return
    
    def _computeHI(self, gridname):

        self.grid = Grid(gridname, self.resolution)
        self.grid.in_rss = self.in_rss
        self.mass = self.hih2file[gridname][:] #already in solar masses
        if self.use_cicw:
            self.grid.CICW(self.pos, self.header['BoxSize'], self.mass)
        else:
            self.grid.CIC(self.pos, self.header['BoxSize'])
        self.saveData()
        return
