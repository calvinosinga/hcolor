#!/usr/bin/env python3
"""

"""

from hicc_library.grid.grid import Grid
from hicc_library.fields.field_super import Field
import h5py as hp
import numpy as np


class galaxy(Field):

    def __init__(self, gd, simname, snapshot, axis, resolution, outfile):
        super().__init__(gd, simname, snapshot, axis, resolution, outfile)

        self.fieldname = 'galaxy'
        self.gridnames = ['blue','red', 'all']
        # we use blue/red/all for every color definition

        # each run will do each color definition provided, but will need a different run to
        # use a different resolution definition.
        self.res_def = gd['%s_use_res']
        self.use_cicw = gd['%s_use_cicw']
        self.use_stmass = gd['%s_use_stmass']
        self.col_defs = list(self.getColorDefinitions().keys())
        
        fields = ['SubhaloStellarPhotometrics','SubhaloPos','SubhaloMassType',
                'SubhaloVel']
        
        data = self._loadGalaxyData(fields)
        self.pos = data['SubhaloPos'][:]
        self.vel = data['SubhaloVel'][:]
        self.gr = data['SubhaloStellarPhotometrics'][:,4] - \
                data['SubhaloStellarPhotometrics'][:,5]
        if self.use_stmass:
            self.mass = data['SubhaloMassType'][:,4] # only using stellar mass here
        else:
            self.mass = np.sum(data['SubhaloMassType'][:], axis=1)
        self.r = data['SubhaloStellarPhotometrics'][:,5]
        self._convertMass()
        self._convertPos()
        self._convertVel()
        return
    
    @staticmethod
    def isRed(gr, stmass, color_dict): #maybe leave gd out?
        b = color_dict['b']
        m = color_dict['m']
        mb = color_dict['mb']
        return gr > b + m * (np.log10(stmass) + mb)
    
    @staticmethod
    def isResolved(stmass, r, res_dict):
        stmass_min = res_dict['stmass']
        stmass_mask = stmass > stmass_min

        r_max = res_dict['r']
        if r_max is None:
            r_mask = np.ones_like(stmass_mask)
        else:
            r_mask = r < r_max

        return stmass_mask * r_mask
    
    @staticmethod
    def getResolutionDefinitions(simname):
        # taken from Pillepich et al 2018, table 1 (in solar masses)
        mean_baryon_cell = {'tng100':1.4e6, 'tng100-2':11.2e6, 'tng100-3':89.2e6,
                'tng300':11e6, 'tng300-2':88e6, 'tng300-3':703e6}
        # the different definitions of what makes a galaxy resolved
        galaxy_min_resolution = {}
        # from papastergis 2013, minimum for galaxies is r-band lum of -17 mag
        galaxy_min_resolution['papa'] = {'r':-17, 'stmass':0}
        # resolution to match hisubhalo
        galaxy_min_resolution['diemer'] = {'r':None, 'stmass':mean_baryon_cell[simname]*200}
        # wolz definition?
        return galaxy_min_resolution
    
    @staticmethod
    def getColorDefinitions():
        # these are what separates the blue/red population, given in the gr-stmass plane.
        # the format is gr > b + m*(log(stmass)+mb)
        galaxy_red_definition = {}
        # from Nelson's definition
        galaxy_red_definition['nelson'] = {'b':0.65, 'm':0.02, 'mb':-10.28}
        # experiments with sensitivy to color definition - translate the above def. vertically
        galaxy_red_definition['nelson_low'] = {'b':0.6, 'm':0.02, 'mb':-10.28}
        galaxy_red_definition['nelson_high'] = {'b':0.7, 'm':0.02, 'mb':-10.28}
        # trying it with a straight gr cut as well
        galaxy_red_definition['straight'] = {'b':0.55, 'm':0, 'mb':0}
        return galaxy_red_definition
    
    def computeGrids(self):
        res_dict = self.getResolutionDefinitions(self.simname)[self.res_def]
        resolved_mask = self.isResolved(self.mass, self.r, res_dict)
        for col in self.col_defs:
            color_dict = self.getColorDefinitions()[col]
            red_mask = self.isRed(self.gr, self.mass, color_dict)
            blue_mask = np.invert(red_mask)
            all_mask = np.ones_like(blue_mask)
            mask_dict = {'red':red_mask*resolved_mask, 
                    'blue':blue_mask*resolved_mask, 
                    'all':all_mask}

            
            for g in self.gridnames:                
                self._computeGal(g+'_'+col, mask_dict[g])
                self.saveData(col)
            
            self._toRedshiftSpace()
            for g in self.gridnames:
                self._computeGal(g+'_'+col+'rs', mask_dict[g])
                self.saveData(col)
        self.gridsave.close()
        return
    
    def computeAux(self):
        return super().computeAux()
    
    def saveData(self, color_def):
        dat = super().saveData()
        dct = dat.attrs
        dct['resolution_definition'] = self.res_def
        dct['color_definition'] = color_def
        dct['is_stmass'] = self.use_stmass
        dct['used_dust'] = False
        dct['is_massden'] = self.use_cicw
        return dat
    
    def _computeGal(self, gridname, mask):
        self.grid = Grid(gridname, self.resolution)
        self.grid.in_rss = self.in_rss

        if self.use_cicw:
            self.grid.CICW(self.pos[mask], self.header['BoxSize'], self.mass[mask])
        else:
            self.grid.CIC(self.pos[mask], self.header['BoxSize'])
        return

class galaxy_dust(galaxy):
    def __init__(self, gd, simname, snapshot, axis, resolution, outfile):
        super().__init__(gd, simname, snapshot, axis, resolution, outfile)
        self.fieldname = 'galaxy_dust'
        dustfile = hp.File(gd['dust'], 'r')
        photo = dustfile['Subhalo_StellarPhot_p07c_cf00dust_res_conv_ns1_rad30pkpc']

        # using the axis to get the closest projection
        proj = dict(photo.attrs['projVecs'])
        los = np.zeros_like(proj)
        los[:, self.axis] += 1

        dist = np.sum((proj-los)**2, axis=1)
        minidx = np.argmin(dist)

        self.gr = photo[:,1,minidx] - photo[:,2, minidx]
        self.r = photo[:,2,minidx]
        return
    
    def saveData(self, color_def):
        dat = super().saveData(color_def)
        dct = dat.attrs
        dct['used_dust'] = True
        return dat

        