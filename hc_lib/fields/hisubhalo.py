#!/usr/bin/env python3
"""

"""

from hc_lib.grid.grid import Grid, VelGrid
from hc_lib.fields.field_super import Field
from hc_lib.grid.grid_props import hisubhalo_grid_props
from hc_lib.fields.run_lib import getMolFracModelsGalH2, getMolFracModelsGalHI
from hc_lib.fields.run_lib import HIResolutionDefinitions
import copy
import h5py as hp
import numpy as np
    
class hisubhalo(Field):

    def __init__(self, simname, snapshot, axis, resolution, pkl_path, verbose,
                shcatpath, hih2filepath, fieldname = 'hisubhalo', runtype = ''):
        
        self.fieldname = fieldname
 
        self.hih2filepath = hih2filepath
        self.loadpath = shcatpath
        self.runtype = runtype
        super().__init__(simname, snapshot, axis, resolution, pkl_path, verbose)
        if self.v:
            print('\nhisubhalo object created, object dictionary:')
            print(self.__dict__)
        return

    def getGridProps(self):
        gridnames = {}
        runtype = self.runtype
        def _addGrids(models, spaces, resolutions, MAS, censat, types = ['vel', 'mass']):
            for m in models:
                for r in resolutions:
                    for M in MAS:
                        for s in spaces:
                            for cs in censat:
                                for tp in types:
                                    if not (tp == 'vel' and s == 'redshift'):
                                        gp = hisubhalo_grid_props(M, self.fieldname,
                                            s, tp, m, r, cs)
                                        gridnames[gp.getH5DsetName()] = gp
        

        if runtype == 'fiducial':

            models = getMolFracModelsGalHI()
            mas = ['CICW']
            spaces = ['redshift', 'real']
            censat = ['both']
            resolutions = ['diemer']
            _addGrids(models, spaces, resolutions, mas, censat)
        
        elif runtype == 'alt_MAS':
            models = getMolFracModelsGalHI()
            mas = ['rCICW', 'CIC']
            spaces = ['redshift', 'real']
            censat = ['both']
            resolutions = ['diemer']
            _addGrids(models, spaces, resolutions, mas, censat)
        
        elif runtype == 'bins_thresholds':
            models = getMolFracModelsGalHI()
            mas = ['CICW']
            spaces = ['redshift', 'real']
            resolutions = []
            for r in list(HIResolutionDefinitions(self.simname).keys()):
                if 'bin' in r or 'threshold' in r:
                    resolutions.append(r)
            if self.simname == 'tng100':
                resolutions.append('tng100-2')
                resolutions.append('tng300')
            censat = ['both', 'centrals', 'satellites']
            _addGrids(models, spaces, resolutions, mas, censat)
        
        elif runtype == 'centrals_test':
            models = getMolFracModelsGalHI()
            mas = ['CICW']
            spaces = ['redshift', 'real']
            resolutions = ['diemer']
            censat = ['centrals', 'satellites', 'both']
            _addGrids(models, spaces, resolutions, mas, censat)
    
        elif runtype == 'censat':
            models = getMolFracModelsGalHI()
            mas = ['CICW']
            spaces = ['redshift', 'real']
            resolutions = ['diemer']
            censat = ['centrals', 'satellites', 'both']
            _addGrids(models, spaces, resolutions, mas, censat)
        
        return gridnames

    def computeGrids(self, outfile):
        super().setupGrids(outfile)

        if self.v:
            print("now computing the grids for hisubhalo...")
        
        hih2file = hp.File(self.hih2filepath, 'r')
        ids = hih2file['id_subhalo'][:] # used to idx into the subhalo catalog
        ids = ids.astype(np.int32)

        fields = ['SubhaloPos', 'SubhaloVel', 'SubhaloMassType']

        data = self._loadGalaxyData(self.loadpath, fields) # implemented in superclass
        ngals = len(data['SubhaloPos'])
        pos = data['SubhaloPos'][ids] # ckpc/h
        vel = data['SubhaloVel'][ids] # km/s
        gal_masses = data['SubhaloMassType'][ids, :]
        gal_masses = self._convertMass(gal_masses)
        pos = self._convertPos(pos)
        centrals = self._loadGroupData(self.loadpath, ['GroupFirstSub'])
        temp = copy.copy(pos)
        rspos = self._toRedshiftSpace(temp, vel)
        del temp
        ############### HELPER METHOD ###############################
        def computeHI(gprop, pos):
            gprop.props['type'] = 'mass'
            grid = Grid(gprop.getH5DsetName(), self.grid_resolution, verbose=self.v)
            
            mass = hih2file[gprop.props['model']][:] #already in solar masses
            mask = self.getResolvedSubhalos(mass, gal_masses, gprop.props['HI_res'])
            if g.props['censat'] == 'centrals':
                censat_mask = np.zeros(ngals, dtype = bool)
                censat_mask[centrals[centrals >= 0]] = True
            elif g.props['censat'] == 'satellites':
                censat_mask = np.ones(ngals, dtype = bool)
                censat_mask[centrals[centrals >= 0]] = False
            else:
                censat_mask = np.ones(ngals, dtype = bool)

            mask = mask & censat_mask[ids]
            grid.runMAS(gprop.props['mas'], pos[mask, :], self.header['BoxSize'], mass[mask])
            
            
            self.saveData(outfile, grid, gprop)
            if self.v:
                print('\nfinished computing a grid, printing its properties...')
                print(grid.print())
            return
        
        def computeVel(gprop, pos, vel):
            gprop.props['type'] = 'vel'
            grid = VelGrid(gprop.getH5DsetName(), self.grid_resolution, verbose = self.v)

            if self.v:
                hs = '#' * 20
                print(hs+" COMPUTE HI VEL FOR %s "%(gprop.getH5DsetName().upper()) + hs)
            
            grid.CICW(pos, self.header['BoxSize'], vel)
            self.saveData(outfile, grid, gprop)
            return
        ###############################################################

        for g in list(self.gridprops.values()):
            if g.props["space"] == 'real':
                pos_arr = pos
                if g.props['type'] == 'vel':
                    computeVel(g, pos_arr, vel)
            elif g.props['space'] == 'redshift':
                pos_arr = rspos
            if g.props['type'] == 'mass':
                computeHI(g, pos_arr)
        
        return

    def getResolvedSubhalos(self, HImass, masstype, resdef):
        resdict = HIResolutionDefinitions(self.simname)[resdef]
        mask = np.ones_like(HImass, dtype=bool)
        for k, v in resdict.items():
            if k == 'HI':
                mask &= (HImass >= v[0]) & (HImass < v[1])
            elif k == 'stmass':
                mask &= (masstype[:, 4] >= v[0]) & (masstype[:, 4] < v[1])
            elif k == 'gas':
                mask &= (masstype[:, 0] >= v[0]) & (masstype[:, 0] < v[1])
        return mask

    def makeSlice(self, grid, grid_props, perc=0.1, mid=None):
        return super().makeSlice(grid, grid_props, perc=perc, mid=mid)

    def _convertVel(self, vel):
        # subhalos' velocities are already in km/s
        return vel

class h2subhalo(hisubhalo):

    def __init__(self, simname, snapshot, axis, resolution, pkl_path, verbose,
                shcatpath, hih2filepath):
        super().__init__(simname, snapshot, axis, resolution, pkl_path, verbose,
                shcatpath, hih2filepath, 'h2subhalo')
        return
    
    def getGridProps(self):
        models = getMolFracModelsGalH2()
        # mas = ['CIC', 'CICW']
        mas = ['CICW']
        spaces = ['redshift', 'real']
        # res = list(HIResolutionDefinitions().keys())
        res = ['diemer']
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

