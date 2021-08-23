#!/usr/bin/env python3
"""

"""

from hicc_library.grid.grid import Grid
from hicc_library.fields.field_super import Field
import h5py as hp
import numpy as np


class galaxy(Field):

    def __init__(self, gd, simname, snapshot, axis, resolution, 
            outfile, fieldname='galaxy'):
        
        super().__init__(gd, simname, snapshot, axis, resolution, outfile)

        self.fieldname = fieldname
        self.gridnames = ['blue','red', 'all']
        # we use blue/red/all for every color definition

        # each run will do each color definition provided, but will need a different run to
        # use a different resolution definition.
        self.use_res = gd['%s_use_res'%self.fieldname]
        self.res_dict = self.getResolutionDefinitions(self.simname)[self.use_res]
        self.use_cicw = gd['%s_use_cicw'%self.fieldname]
        self.use_stmass = gd['%s_use_stmass'%self.fieldname]
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
        resolved_mask = self.isResolved(self.mass, self.r, self.res_dict)
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

        
        # now doing redshift-space grids
        self._toRedshiftSpace()
        for col in self.col_defs:
            color_dict = self.getColorDefinitions()[col]
            red_mask = self.isRed(self.gr, self.mass, color_dict)
            blue_mask = np.invert(red_mask)
            all_mask = np.ones_like(blue_mask)
            mask_dict = {'red':red_mask*resolved_mask, 
                    'blue':blue_mask*resolved_mask, 
                    'all':all_mask}
            
            for g in self.gridnames:
                self._computeGal(g+'_'+col, mask_dict[g]) # rs added in grid's save method
                self.saveData(col)

        self.outfile.close()
        return
    
    def computeAux(self):
        return super().computeAux()
    
    def saveData(self, color_def):
        dat = super().saveData()
        dct = dat.attrs
        dct['use_res'] = self.use_res
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
        if 'nelson' not in gridname:
            self.grid.ignoreGrid()
        return

class galaxy_dust(galaxy):
    def __init__(self, gd, simname, snapshot, axis, resolution, outfile):
        super().__init__(gd, simname, snapshot, axis, resolution, 
                outfile, 'galaxy_dust')
        
        dustfile = hp.File(gd['dust'], 'r')
        photo = dustfile['Subhalo_StellarPhot_p07c_cf00dust_res_conv_ns1_rad30pkpc']

        # using the axis to get the closest projection
        proj = dict(photo.attrs)['projVecs']
        los = np.zeros_like(proj)
        los[:, self.axis] += 1

        dist = np.sum((proj-los)**2, axis=1)
        minidx = np.argmin(dist)

        self.gr = photo[:,1,minidx] - photo[:,2, minidx]
        self.r = photo[:,2,minidx]
        dustfile.close()
        return
    
    def saveData(self, color_def):
        dat = super().saveData(color_def)
        dct = dat.attrs
        dct['used_dust'] = True
        return dat
    

from hydrotools.interface import interface as iface_run

class galaxy_ptl(galaxy):

    def __init__(self, gd, simname, snapshot, axis, resolution, outfile):
        super().__init__(gd, simname, snapshot, axis, resolution,
                outfile, 'galaxy_ptl')
        self.gridnames = ['blue','red','blue_dust', 'red_dust']
        
        if gd['use_ht']:
            self._useHydrotools(gd)
        
        self.ht_file = hp.File(gd['ht_path'], 'r')
        self.gr = self.ht_file['gr_normal']
        self.gr_dust = self.ht_file['gr_dust']

        self.col = gd['%s_col_def'%self.fieldname]

        if self.use_stmass:
            self.ptl_names = ['ptlstr']
            self.mass = self.ht_file['catsh_SubhaloMassType'][:,4]
        else:
            self.ptl_names = ['ptlstr','ptlgas','ptldm']
            self.mass = np.sum(self.ht_file['catsh_SubhaloMassType'][:], axis=1)
            # if black holes are implemented use the following definition
            # self.ptl_names = ['ptlstr','ptlgas','ptldm', 'ptlbh']
        
        self.pos = self.ht_file['catsh_SubhaloPos'] * self.header['Time'] # given ckpc, moved to kpc
        self.vel = self.ht_file['catsh_SubhaloVel']
        
        self.use_cicw = 1 # this should always use CICW
        return
    # ['catgrp_GroupNsubs', 'catgrp_Group_M_Crit200', 'catgrp_id', 'catgrp_is_primary', 'catsh_gr_normal',
    #  'catsh_id', 'catxt_gr_dust', 'config', 'ptldm_Coordinates', 'ptldm_ParticleIDs', 'ptldm_Velocities',
    #   'ptldm_first', 'ptldm_n', 'ptlgas_Coordinates', 'ptlgas_ParticleIDs', 'ptlgas_Velocities', 
    #   'ptlgas_first', 'ptlgas_n', 'ptlstr_Coordinates', 'ptlstr_ParticleIDs', 'ptlstr_Velocities', 
    #   'ptlstr_first', 'ptlstr_n']

    
    def _loadSlices(self, fptl):
        
        shslc = []
        for i in range(len(fptl-1)):
            shslc.append(slice(fptl[i],fptl[i+1]))
        shslc.append(slice(fptl[-1], -1))
        return shslc
    
    def _useHydrotools(self, gd):
        ht_suf = gd['ht_suf']

        xtf = ['gr_dust']
        shf = ['gr_normal', 'SubhaloPos', 'SubhaloVel', 'SubhaloMassType']
        ptf = ['Coordinates', 'Velocities', 'ParticleIDs', 'Masses']
        sim = self._get_simname_as_ht_input(self.simname)
        if self.use_stmass:
            iface_run.extractGalaxyData(sim=sim, snap_idx=self.snapshot, verbose = bool(self.v),
                    file_suffix=ht_suf, output_compression='gzip', catxt_get=True, catxt_fields=xtf,
                    catsh_get=True, catsh_fields=shf, ptlstr_get=True, ptlstr_fields=ptf,
                    output_path=gd['results'], catgrp_get = False)
        else:
            iface_run.extractGalaxyData(sim=sim, snap_idx=self.snapshot, verbose = bool(self.v),
                    file_suffix=ht_suf, output_compression='gzip', catxt_get=True, catxt_fields=xtf,
                    catsh_get=True, catsh_fields=shf, ptlstr_get=True, ptlstr_fields=ptf,
                    ptldm_get=True, ptldm_fields=ptf, ptlgas_get=True, ptlgas_fields=ptf,
                    output_path=gd['results'], catgrp_get = False)
    
        return
    
    
    @staticmethod
    def _get_simname_as_ht_input(simname):
        # since ht uses different keywords for simnames, include this
        # dictionary to traverse between the two
        ht_sim = {'tng100':'tng75', 'tng300':'tng205', 'tng50':'tng35'}

        return ht_sim[simname]
    
    def _getMasks(self):
        masks = []
        resolved_mask = self.isResolved(self.mass, self.r, self.res_dict)
        col_def = self.getColorDefinitions()[self.col]
        for g in self.gridnames:
            if 'dust' in g:
                gr = self.gr_dust
            else:
                gr = self.gr
            
            if 'red' in g:
                mask = self.isRed(gr, self.mass, col_def)
            else:
                mask = np.invert(self.isRed(gr, self.mass, col_def))
            
            mask *= resolved_mask
            masks.append(mask)
            

        return masks
    
    def computeGrids(self):
        # figure out which subhalos are red/blue
        # need to do this first to avoid having multiple grid arrays which take a lot of memory
        masks = self._getMasks()
        ht = self.ht_file
        # iterate over each grid, use the mask to figure out
        # which data that you want to add to the grid 
        for i in range(len(self.gridnames)):
            mask = masks[i]
            gn = self.gridnames[i]
            
            self.grid = Grid(gn, self.resolution)
            # mask off the subhalos not included in this color definition
            shpos = self.pos[mask, :]
            # for each particle type
            for p in self.ptl_names:
                # load the data for this particle type
                ptlpos = ht['%s_Coordinates'%p]
                ptlmass = ht['%s_Masses'%p]

                ptlslc = self._loadSlices(ht['%s_first'])
                # iterate over each subhalo, placing the particles into the grid
                for s in range(len(shpos)):
                    # the positions are relative to the subhalos position
                    pos_for_grid = ptlpos[ptlslc[s], :] + shpos[s, :]
                    mass_for_grid = ptlmass[ptlslc[s]]
                    self.grid.CICW(pos_for_grid, self.header['BoxSize'], mass_for_grid)
            self.saveData(gn)
                
        
        # now do the same in redshift space
        for i in range(len(self.gridnames)):
            mask = masks[i]
            gn = self.gridnames[i]
            
            self.grid = Grid(gn, self.resolution)
            self.grid.toRSS()
            # mask off the subhalos not included in this color definition
            shpos = self.pos[mask, :]
            shvel = self.vel[mask, :]
            # for each particle type
            for p in self.ptl_names:
                # load the data for this particle type
                ptlpos = ht['%s_Coordinates'%p]
                ptlmass = ht['%s_Masses'%p]
                ptlvel = ht['%s_Velocities'%p]

                ptlslc = self._loadSlices(ht['%s_first'])
                # iterate over each subhalo, placing the particles into the grid
                for s in range(len(shpos)):
                    # the positions are relative to the subhalos position
                    pos_for_grid = ptlpos[ptlslc[s], :] + shpos[s, :]
                    vel_for_grid = ptlvel[ptlslc[s], :] + shvel[s, :]
                    mass_for_grid = ptlmass[ptlslc[s]]
                    self._toRedshiftSpace(pos_for_grid, vel_for_grid)
                    self.grid.CICW(pos_for_grid, self.header['BoxSize'], mass_for_grid)
            self.saveData(gn)
        return

    def saveData(self, gridname):
        dat = super().saveData(self.col)
        dct = dat.attrs
        dct['use_res'] = self.use_res
        dct['is_stmass'] = self.use_stmass
        if 'dust' in gridname:
            dct['used_dust'] = True
        else:
            dct['used_dust'] = False
        dct['is_massden'] = 1
        return 