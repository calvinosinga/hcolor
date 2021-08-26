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
        self.hih2filepath = gd['post']+'hih2_galaxy_%03d.hdf5'%snapshot
        if self.v:
            print('\nhisubhalo object created, object dictionary:')
            print(self.__dict__)
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
        if self.v:
            print("now computing the grids for hisubhalo...")
        hih2file = hp.File(self.hih2filepath, 'r')
        
        ids = hih2file['id_subhalo'][:] # used to idx into the subhalo catalog
        ids = ids.astype(np.int32)

        fields = ['SubhaloPos', 'SubhaloVel']

        data = self._loadGalaxyData(fields) # implemented in superclass
        pos = data['SubhaloPos'][ids] # ckpc/h
        vel = data['SubhaloVel'][ids] # km/s

        pos = self._convertPos(pos)

        in_rss = False
        ############### HELPER METHOD ###############################
        def computeHI(gridname):
            grid = Grid(gridname, self.resolution)
            grid.in_rss = in_rss
            mass = hih2file[gridname][:] #already in solar masses
            if self.use_cicw:
                grid.CICW(pos, self.header['BoxSize'], mass)
            else:
                grid.CIC(pos, self.header['BoxSize'])
            self.saveData(grid)
            if self.v:
                print('\nhisubhalo %s')
                print(grid.print())
            return
        ###############################################################

        for g in self.gridnames:
            computeHI(g)
        
        pos = self._toRedshiftSpace(pos, vel)
        in_rss = True
        for g in self.gridnames:
            computeHI(g)
        
        self.outfile.close()
        # h5py files cannot be pickled, this file is not needed after this
        del self.outfile

        return

