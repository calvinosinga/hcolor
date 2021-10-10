#!/usr/bin/env python3
"""

"""

from hicc_library.grid.grid import Grid
from hicc_library.fields.field_super import Field, grid_props
import h5py as hp
import numpy as np

class hisubhalo_grid_props(grid_props):

    def __init__(self, base, mas, field, resdef):
        other = {}
        self.model = base
        
        other['resdef'] = resdef
        super().__init__(base, mas, field, other)
    
    def isIncluded(self):
        def test(schts):
            mastest = self.props['mas'] in schts
            return mastest
            
        sp = self.props
        if sp['resdef'] == 'papa':
            mas = ['CIC']
            return test(mas)

        return True
    
    def isCompatible(self, other):
        sp = self.props
        op = other.props

        if sp['resdef'] == 'papa':
            papa_fields = ['galaxy', 'galaxy_dust']
            return sp['resdef'] == op['resdef'] and op['field'] in papa_fields
        
        return super().isCompatible(other)
    
class hisubhalo(Field):

    def __init__(self, simname, snapshot, axis, resolution, pkl_path, verbose,
                shcatpath, hih2filepath, fieldname = 'hisubhalo'):
        super().__init__(simname, snapshot, axis, resolution, pkl_path, verbose)
        self.fieldname = fieldname
 
        self.hih2filepath = hih2filepath
        self.loadpath = shcatpath
        if self.v:
            print('\nhisubhalo object created, object dictionary:')
            print(self.__dict__)
        return
    
    def getGridProps(self):
        models = self.getMolFracModelsGal()
        mas = ['CIC', 'CICW']
        res = list(self.getResolutionDefinitions().keys())
        grp = {}
        for m in models:
            for s in mas:
                for r in res:
                    gp = hisubhalo_grid_props(m, s, self.fieldname, r)
                    if gp.isIncluded():
                        grp[gp.getName()] = gp
        return grp
    @staticmethod
    def getResolutionDefinitions():
        # taken from Pillepich et al 2018, table 1 (in solar masses)
        mean_baryon_cell = {'tng100':1.4e6, 'tng100-2':11.2e6, 'tng100-3':89.2e6,
                'tng300':11e6, 'tng300-2':88e6, 'tng300-3':703e6}
        res_defs = {}
        res_defs['papa'] = {'HI':(10**7.5, np.inf)} 
        res_defs['diemer'] = {'HI':(0, np.inf)} # by default, already implemented on data
        
        # there is a linewidths restriction, unsure how to approach that in papastergis
        # wolz is intensity map so no minimum threshold
        return res_defs
        

    @staticmethod
    def getMolFracModelsGal():
        """
        Returns a list of the molecular fraction models provided by Diemer+ 2018,
        specifically the ones that correspond to the subhalo catalog.
        """
        models = ['GD14','GK11','K13','S14']
        proj = ['map','vol']
        modelnames = []
        for m in models:
            for p in proj:
                modelnames.append('m_hi_%s_%s'%(m,p))
        modelnames.append('m_hi_L08_map')
        return modelnames
    

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
        def computeHI(gprop, pos, is_in_rss):
            grid = Grid(gprop.getName(), self.resolution, verbose=self.v)
            if is_in_rss:
                grid.toRSS()

            mass = hih2file[gprop.model][:] #already in solar masses
            if gprop.props['resdef'] == 'papa':
                mask = self.getResolvedSubhalos(mass, gprop.props['resdef'])
            else:
                mask = np.ones_like(mass)
            if gprop.props['mas'] == 'CICW':
                grid.CICW(pos[mask, :], self.header['BoxSize'], mass[mask])
            else:
                grid.CIC(pos[mask, :], self.header['BoxSize'])
            

            self.saveData(outfile, grid, gprop)
            if self.v:
                print('\nfinished computing a grid, printing its properties...')
                print(grid.print())
            return
        ###############################################################

        for g in list(self.gridprops.values()):
            computeHI(g, pos, in_rss)
        
        pos = self._toRedshiftSpace(pos, vel)
        in_rss = True
        for g in list(self.gridprops.values()):
            computeHI(g, pos, in_rss)
        
        return

    def getResolvedSubhalos(self, mass, resdef):
        resdict = self.getResolutionDefinitions()[resdef]
        mask = np.ones_like(mass)
        for k, v in resdict.items():
            if k == 'HI':
                mask *= (mass >= v[0]) & (mass < v[1])
        return mask



    def _convertVel(self, vel):
        # subhalos' velocities are already in km/s
        return vel

class h2subhalo(hisubhalo):

    def __init__(self, simname, snapshot, axis, resolution, pkl_path, verbose,
                shcatpath, hih2filepath):
        super().__init__(simname, snapshot, axis, resolution, pkl_path, verbose,
                shcatpath, hih2filepath, 'h2subhalo')
        return
    
    def computeGrids(self, outfile):
        ############ FROM FIELD_SUPER CLASS #######################################
        if self.header is None:
            raise ValueError("header needs to be loaded before computing grids")
        dat = outfile.create_dataset('pickle', data=[0])
        dat.attrs['path'] = self.pkl_path
        if self.v:
            print("the saved pickle path: %s"%self.pkl_path)

        if self.v:
            print("now computing the grids for h2subhalo...")
        #########################################################################

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
        def computeH2(gprop, pos, is_in_rss):
            grid = Grid(gprop.getName(), self.resolution, verbose=self.v)
            if is_in_rss:
                grid.toRSS()
            mass = hih2file[gprop.model][:] #already in solar masses
            if gprop.props['mas'] == 'CICW':
                grid.CICW(pos, self.header['BoxSize'], mass)
            else:
                grid.CIC(pos, self.header['BoxSize'])
            self.saveData(outfile, grid, gprop)
            if self.v:
                print('\nfinished computing a grid, printing its properties...')
                print(grid.print())
            return
        ###############################################################

        for g in list(self.gridprops.values()):
            computeH2(g, pos, in_rss)
        
        pos = self._toRedshiftSpace(pos, vel)
        in_rss = True
        for g in list(self.gridprops.values()):
            computeH2(g, pos, in_rss)
        
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
