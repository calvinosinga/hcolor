#!/usr/bin/env python3
"""

"""

from hc_lib.grid.grid import Grid
from hc_lib.fields.field_super import Field
from hc_lib.grid.grid_props import hisubhalo_grid_props
import copy
import h5py as hp
import numpy as np

def getResolutionDefinitions():
    # taken from Pillepich et al 2018, table 1 (in solar masses)
    mean_baryon_cell = {'tng100':1.4e6, 'tng100-2':11.2e6, 'tng100-3':89.2e6,
            'tng300':11e6, 'tng300-2':88e6, 'tng300-3':703e6}
    res_defs = {}
    res_defs['papastergis_ALFALFA'] = {'HI':(10**7.5, np.inf)} 
    res_defs['diemer'] = {'HI':(0, np.inf)} # by default, already implemented on data
    
    # there is a linewidths restriction, unsure how to approach that in papastergis
    # wolz is intensity map so no minimum threshold
    return res_defs
    

def getMolFracModelsGalHI():
    """
    Returns a list of the molecular fraction models provided by Diemer+ 2018,
    specifically the ones that respond to the subhalo catalog.
    """
    models = ['GD14','GK11','K13','S14']
    proj = ['map','vol']
    modelnames = []
    for m in models:
        for p in proj:
            modelnames.append('m_hi_%s_%s'%(m,p))
    modelnames.append('m_hi_L08_map')
    return modelnames

    
def getMolFracModelsGalH2():
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

    
class hisubhalo(Field):

    def __init__(self, simname, snapshot, axis, resolution, pkl_path, verbose,
                shcatpath, hih2filepath, fieldname = 'hisubhalo'):
        
        self.fieldname = fieldname
 
        self.hih2filepath = hih2filepath
        self.loadpath = shcatpath
        
        super().__init__(simname, snapshot, axis, resolution, pkl_path, verbose)
        if self.v:
            print('\nhisubhalo object created, object dictionary:')
            print(self.__dict__)
        return
    
    def getGridProps(self):
        models = getMolFracModelsGalHI()
        mas = ['CIC', 'CICW']
        spaces = ['redshift', 'real']
        res = list(getResolutionDefinitions().keys())
        grp = {}
        for m in models:
            for s in spaces:
                for r in res:
                    for M in mas:
                        gp = hisubhalo_grid_props(M, self.fieldname, s, m, r)
                        if gp.isIncluded():
                            grp[gp.getH5DsetName()] = gp
        return grp
    

    def computeGrids(self, outfile):
        super().setupGrids(outfile)

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

        temp = copy.copy(pos)
        rspos = self._toRedshiftSpace(temp, vel)
        del temp, vel
        ############### HELPER METHOD ###############################
        def computeHI(gprop, pos):
            grid = Grid(gprop.getH5DsetName(), self.grid_resolution, verbose=self.v)

            mass = hih2file[gprop.props['model']][:] #already in solar masses
            if gprop.props['HI_res'] == 'papa':
                mask = self.getResolvedSubhalos(mass, gprop.props['HI_res'])
            else:
                mask = np.ones_like(mass, dtype=bool)
            if gprop.props['mas'] == 'CICW':
                if not np.issubdtype(mask[0], bool):
                    mask = mask.astype('bool')
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
            if g.props["space"] == 'real':
                pos_arr = pos
            elif g.props['space'] == 'redshift':
                pos_arr = rspos
            computeHI(g, pos_arr)
        
        return

    def getResolvedSubhalos(self, mass, resdef):
        resdict = getResolutionDefinitions()[resdef]
        mask = np.ones_like(mass, dtype=bool)
        for k, v in resdict.items():
            if k == 'HI':
                mask *= (mass >= v[0]) & (mass < v[1])
        return mask

    def makeSlice(self, grid, perc=0.1, mid=None, avg=True):
        return super().makeSlice(grid, perc=perc, mid=mid, avg=avg)

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
        super().setupGrids(outfile)

        hih2file = hp.File(self.hih2filepath, 'r')
        ids = hih2file['id_subhalo'][:] # used to idx into the subhalo catalog
        ids = ids.astype(np.int32)

        fields = ['SubhaloPos', 'SubhaloVel']

        data = self._loadGalaxyData(self.loadpath, fields) # implemented in superclass
        pos = data['SubhaloPos'][ids] # ckpc/h
        vel = data['SubhaloVel'][ids] # km/s

        pos = self._convertPos(pos)
        temp = copy.copy(pos)
        rspos = self._toRedshiftSpace(temp, vel)
        del temp, vel

        ############### HELPER METHOD ###############################
        def computeH2(gprop, pos):
            grid = Grid(gprop.getH5DsetName(), self.grid_resolution, verbose=self.v)

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
            if g.props['space'] == 'real':
                pos_arr = pos
            elif g.props['space'] == 'redshift':
                pos_arr = rspos
            computeH2(g, pos_arr)
        
        return

