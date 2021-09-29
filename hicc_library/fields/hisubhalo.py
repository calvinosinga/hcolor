#!/usr/bin/env python3
"""

"""

from numpy.lib.utils import info
from hicc_library.grid.grid import Grid
from hicc_library.fields.field_super import Field
import h5py as hp
import numpy as np

class hisubhalo(Field):

    def __init__(self, simname, snapshot, axis, resolution, pkl_path, verbose,
                shcatpath, hih2filepath):
        super().__init__(simname, snapshot, axis, resolution, pkl_path, verbose)
        self.fieldname = 'hisubhalo'
        self.gridnames = self.getMolFracModelsGal()
 
        self.use_cicw = True
        self.hih2filepath = hih2filepath
        self.loadpath = shcatpath
        if self.v:
            print('\nhisubhalo object created, object dictionary:')
            print(self.__dict__)
        return
    
    @staticmethod
    def getResolutionDefinitions():
        # taken from Pillepich et al 2018, table 1 (in solar masses)
        mean_baryon_cell = {'tng100':1.4e6, 'tng100-2':11.2e6, 'tng100-3':89.2e6,
                'tng300':11e6, 'tng300-2':88e6, 'tng300-3':703e6}
        res_defs = {}
        res_defs['papa'] = {'HI':(10**7.5, np.inf)}

        # wolz is intensity map so no minimum threshold
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
    
    def useCIC(self):
        self.use_cicw = False
        return
    
    def computeGrids(self, outfile):
        super().computeGrids(outfile)

        if self.v:
            print("now computing the grids for hisubhalo...")
        
        hih2file = hp.File(self.hih2filepath, 'r')
        ids = hih2file['id_subhalo'][:] # used to idx into the subhalo catalog
        ids = ids.astype(np.int32)

        fields = ['SubhaloPos', 'SubhaloVel']

        data = self._loadGalaxyData(self.loadpath, fields) # implemented in superclass
        pos = data['SubhaloPos'][ids] # ckpc/h
        vel = data['SubhaloVel'][ids] # km/s

        pos = self._convertPos(pos)

        in_rss = False
        ############### HELPER METHOD ###############################
        def computeHI(gridname):
            grid = Grid(gridname, self.resolution, verbose=self.v)
            grid.in_rss = in_rss
            mass = hih2file[gridname][:] #already in solar masses
            if self.use_cicw:
                grid.CICW(pos, self.header['BoxSize'], mass)
            else:
                grid.CIC(pos, self.header['BoxSize'])
            self.saveData(outfile, grid)
            if self.v:
                print('\nfinished computing a grid, printing its properties...')
                print(grid.print())
            return
        ###############################################################

        for g in self.gridnames:
            computeHI(g)
        
        pos = self._toRedshiftSpace(pos, vel)
        in_rss = True
        for g in self.gridnames:
            computeHI(g)
        
        return

    def _convertVel(self, vel):
        # subhalos' velocities are already in km/s
        return vel

class h2subhalo(hisubhalo):

    def __init__(self, simname, snapshot, axis, resolution, pkl_path, verbose,
                shcatpath, hih2filepath):
        super().__init__(self, simname, snapshot, axis, resolution, pkl_path, verbose,
                shcatpath, hih2filepath)
        self.fieldname = 'h2subhalo'
        return
    
    def computeGrids(self, outfile):
        super().computeGrids(outfile)

        if self.v:
            print("now computing the grids for hisubhalo...")
        
        hih2file = hp.File(self.hih2filepath, 'r')
        ids = hih2file['id_subhalo'][:] # used to idx into the subhalo catalog
        ids = ids.astype(np.int32)

        fields = ['SubhaloPos', 'SubhaloVel']

        data = self._loadGalaxyData(self.loadpath, fields) # implemented in superclass
        pos = data['SubhaloPos'][ids] # ckpc/h
        vel = data['SubhaloVel'][ids] # km/s

        pos = self._convertPos(pos)

        in_rss = False
        ############### HELPER METHOD ###############################
        def computeH2(gridname):
            grid = Grid(gridname, self.resolution, verbose=self.v)
            grid.in_rss = in_rss
            mass = hih2file[gridname][:] #already in solar masses
            if self.use_cicw:
                grid.CICW(pos, self.header['BoxSize'], mass)
            else:
                grid.CIC(pos, self.header['BoxSize'])
            self.saveData(outfile, grid)
            if self.v:
                print('\nfinished computing a grid, printing its properties...')
                print(grid.print())
            return
        ###############################################################

        for g in self.gridnames:
            computeH2(g)
        
        pos = self._toRedshiftSpace(pos, vel)
        in_rss = True
        for g in self.gridnames:
            computeH2(g)
        
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
                gridnames.append('m_h2_%s_%s'%(m,p))
        gridnames.append('m_h2_L08_map')
        return gridnames