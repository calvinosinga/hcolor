#!/usr/bin/env python3
"""

"""

from hicc_library.grid.grid import Grid
from hicc_library.fields.field_super import Field
import h5py as hp
import numpy as np


class galaxy(Field):

    def __init__(self, simname, snapshot, axis, resolution, 
            pkl_path, verbose, catshpath, fieldname='galaxy'):
        
        super().__init__(simname, snapshot, axis, resolution, pkl_path, verbose)

        self.fieldname = fieldname
        self.gridnames = ['blue','red', 'resolved', 'all']
        # we use blue/red/all for every color definition

        # each run will do each color definition provided, but will need a different run to
        # use a different resolution definition.
        self.use_res = 'diemer'
        self.res_dict = self.getResolutionDefinitions(self.simname)[self.use_res]
        self.use_cicw = True
        self.use_stmass = True
        self.col_defs = list(self.getColorDefinitions().keys())

        self.isHI = False

        self.has_resolved = False

        self.loadpath = catshpath
        if self.v:
            print('%s class variables:'%self.fieldname)
            print('Resolution definition: %s'%self.use_res)
            print('Resolution dictionary: %s'%str(self.res_dict))
            print('Is it using CICW?: %d'%self.use_cicw)
            print('Is it using stellar mass?: %d'%self.use_stmass)
            print('Color definitions:')
            print(self.col_defs)
        return
    
    @staticmethod
    def isRed(gr, stmass, color_dict): #maybe leave gd out?
        if isinstance(color_dict, dict):
            b = color_dict['b']
            m = color_dict['m']
            mb = color_dict['mb']
            return gr > b + m * (np.log10(stmass) + mb)
        else:
            if color_dict:
                return np.ones_like(gr)
            else:
                return np.zeros_like(gr)
    
    @staticmethod
    def isResolved(stmass, photo, res_dict):
        ################ HELPER METHODS #############################
        def gr_elg():
            mn = -0.068*photo['rz']+0.457
            mx = 0.112*photo['rz']+1.901

            return (photo['gr'] > mn) & (photo['gr'] < mx)
        
        def rz_elg():
            mn = 0.218*photo['gr'] + 0.571
            mx = -0.555*photo['gr']+1.901

            return (photo['rz'] > mn) & (photo['rz'] < mx)
        
        ##############################################################


        resolved = np.ones_like(stmass, dtype=bool)

        for r in res_dict:
            if r == 'stmass':
                t = res_dict[r]
                stmass_resolved = (stmass > t[0]) & (stmass < t[1])
                resolved *= stmass_resolved
            else:
                t = res_dict[r]
                if t == 'gr_elg':
                    photo_resolved = gr_elg()
                elif t == 'rz_elg':
                    photo_resolved = rz_elg()
                else:
                    photo_resolved = (photo[r] > t[0]) & (photo[r] < t[1])
                resolved *= photo_resolved
        
        return resolved
    
    @staticmethod
    def getResolutionDefinitions(simname):
        # taken from Pillepich et al 2018, table 1 (in solar masses)
        mean_baryon_cell = {'tng100':1.4e6, 'tng100-2':11.2e6, 'tng100-3':89.2e6,
                'tng300':11e6, 'tng300-2':88e6, 'tng300-3':703e6}
        # papastergis: z=.0023-0.05
        # wolz: z=0.6-1.0


        # the different definitions of what makes a galaxy resolved
        galaxy_min_resolution = {}
        # from papastergis 2013, minimum for galaxies is r-band lum of -17 mag
        galaxy_min_resolution['papa'] = {'r':(-np.inf,-17)}
        # papastergis makes an additional cut (i-z) > -0.25, but states that
        # this cut eliminates a small number of misidentified galaxies by the 
        # SDSS pipeline

        # resolution to match hisubhalo
        galaxy_min_resolution['diemer'] = {'stmass':(mean_baryon_cell[simname]*200, np.inf)}

        # wigglez isn't a good comparison, TNG doesn't have any equivalent UV
        # filters and wigglez has poor r definition (from wolz)
        galaxy_min_resolution['wigglez'] = {'r':(20,22)}
        
        # eBOSS Emission line galaxies
        galaxy_min_resolution['eBOSS_ELG'] = {'g':(21.825,22.825), 'gr':'gr_elg', 
                'rz':'rz_elg'}
        # since gr and rz depend on other values, use strings to indicate a method
        # to use in the resolution definition

        galaxy_min_resolution['eBOSS_LRG'] = {'i':(19.9,21.8), 'z':(-np.inf, 19.95),
                'ri':(0.98, np.inf)}
        # I still need to check if there is an equivalent band for IRACI in TNG
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

        # galaxy_red_definition['eBOSS_ELG'] = False
        # galaxy_red_definition['eBOSS_LRG'] = True
        return galaxy_red_definition
    
    def useAllMass(self):
        self.use_stmass = False
        return
    
    def useCIC(self):
        self.use_cicw = False
        return
    
    def useResolution(self, res_def):
        self.use_res = res_def
        self.res_dict = self.getResolutionDefinitions(self.simname)[self.use_res]
        return
    
    
    def _loadGalaxyData(self, simpath, fields):
        data = super()._loadGalaxyData(simpath, fields)
        pos = data['SubhaloPos'][:]
        vel = data['SubhaloVel'][:]

        photo = data['SubhaloStellarPhotometrics'][:]

        if self.use_stmass:
            mass = data['SubhaloMassType'][:,4] # only using stellar mass here
        else:
            mass = np.sum(data['SubhaloMassType'][:], axis=1)
        
        photo_dict = {}
        photo_dict['gr'] = photo[:, 4] - photo[:, 5]
        photo_dict['r'] = photo[:, 5]
        photo_dict['i'] = photo[:, 6]
        photo_dict['z'] = photo[:, 7]
        photo_dict['g'] = photo[:, 4]
        photo_dict['ri'] = photo_dict['r'] - photo_dict['i']
        photo_dict['rz'] = photo_dict['r'] - photo_dict['z']
        mass = self._convertMass(mass)
        pos = self._convertPos(pos)
        vel = self._convertVel(vel)
        return pos, vel, mass, photo_dict

    def computeGrids(self, outfile):
        ########################## HELPER FUNCTION ###############################
        def computeGal(pos, mass, gridname):
            grid = Grid(gridname, self.resolution, verbose=self.v)
            grid.in_rss = in_rss

            if self.use_cicw:
                grid.CICW(pos, self.header['BoxSize'], mass)
            else:
                grid.CIC(pos, self.header['BoxSize'])
            
            if 'nelson' not in gridname:
                grid.ignoreGrid()
            return grid
        ###########################################################################

        super().computeGrids(outfile)
        fields = ['SubhaloStellarPhotometrics','SubhaloPos','SubhaloMassType',
                'SubhaloVel']
                
        pos, vel, mass, photo = self._loadGalaxyData(self.loadpath, fields)

        gr = photo['gr']

        resolved_mask = self.isResolved(mass, photo, self.res_dict)
        in_rss = False
        for col in self.col_defs:
            color_dict = self.getColorDefinitions()[col]
            red_mask = self.isRed(gr, mass, color_dict)
            blue_mask = np.invert(red_mask)
            all_mask = np.ones_like(blue_mask)
            mask_dict = {'red':red_mask*resolved_mask, 
                    'blue':blue_mask*resolved_mask, 
                    'resolved':resolved_mask,
                    'all':all_mask}

            
            for g in self.gridnames:     
                mask = mask_dict[g]           
                grid = computeGal(pos[mask, :], mass[mask], g+'_'+col)
                self.saveData(outfile, grid, col)
                del grid

        
        # now doing redshift-space grids
        pos = self._toRedshiftSpace(pos, vel)
        in_rss = True
        for col in self.col_defs:
            color_dict = self.getColorDefinitions()[col]
            red_mask = self.isRed(gr, mass, color_dict)
            blue_mask = np.invert(red_mask)
            all_mask = np.ones_like(blue_mask)
            mask_dict = {'red':red_mask*resolved_mask, 
                    'blue':blue_mask*resolved_mask,
                    'resolved':resolved_mask, 
                    'all':all_mask}
            
            for g in self.gridnames:
                mask = mask_dict[g]
                grid = computeGal(pos[mask], mass[mask], g+'_'+col) # rs added in grid's save method
                self.saveData(outfile, grid, col)
                del grid

        return
    
    def computeAux(self):
        return super().computeAux()
    
    def saveData(self, outfile, grid, color_def):
        dat = super().saveData(outfile, grid)
        dct = dat.attrs
        # since the color_definition is on a grid-by-grid basis
        # want to save it to the attrs of the grid itself
        dct['color_definition'] = color_def
        return dat
    
    def _convertVel(self, vel):
        # subhalos' velocities are already in km/s
        return vel
    

    

class galaxy_dust(galaxy):
    def __init__(self, simname, snapshot, axis, resolution, pkl_path, verbose,
            catshpath, dustpath):
        super().__init__(simname, snapshot, axis, resolution, 
                pkl_path, verbose, catshpath, 'galaxy_dust')
        self.dustpath = dustpath
        return
    
    def _loadGalaxyData(self, simpath, fields):
        pos, vel, mass, photo = super()._loadGalaxyData(simpath, fields)
        dustfile = hp.File(self.dustpath, 'r')

        photo = dustfile['Subhalo_StellarPhot_p07c_cf00dust_res_conv_ns1_rad30pkpc']

        # using the axis to get the closest projection
        proj = dict(photo.attrs)['projVecs']
        los = np.zeros_like(proj)
        los[:, self.axis] += 1

        dist = np.sum((proj-los)**2, axis=1)
        minidx = np.argmin(dist)
        
        photo_dict = {}
        photo_dict['gr'] = photo[:, 1, minidx] - photo[:, 2, minidx]
        photo_dict['r'] = photo[:, 2, minidx]
        photo_dict['i'] = photo[:, 3, minidx]
        photo_dict['z'] = photo[:, 4, minidx]
        photo_dict['g'] = photo[:, 4]
        photo_dict['ri'] = photo_dict['r'] - photo_dict['i']
        photo_dict['rz'] = photo_dict['r'] - photo_dict['z']
        dustfile.close()
        return pos, vel, mass, photo_dict
        

    def saveData(self, outfile, grid, color_def):
        dat = super().saveData(outfile, grid, color_def)
        dct = dat.attrs
        dct['used_dust'] = True
        return dat
    

# from hydrotools.interface import interface as iface_run

# class galaxy_ptl(galaxy):

#     def __init__(self, simname, snapshot, axis, resolution, pkl_path, verbose):
#         super().__init__(simname, snapshot, axis, resolution,
#                 pkl_path, verbose, 'galaxy_ptl')
#         self.gridnames = ['blue','red','blue_dust', 'red_dust']
        
        

#         if self.use_stmass:
#             self.ptl_names = ['ptlstr']
#             self.mass = self.ht_file['catsh_SubhaloMassType'][:,4]
#         else:
#             self.ptl_names = ['ptlstr','ptlgas','ptldm']
#             self.mass = np.sum(self.ht_file['catsh_SubhaloMassType'][:], axis=1)
#             # if black holes are implemented use the following definition
#             # self.ptl_names = ['ptlstr','ptlgas','ptldm', 'ptlbh']
        
#         self.pos = self.ht_file['catsh_SubhaloPos'] * self.header['Time'] # given ckpc, moved to kpc
#         self.vel = self.ht_file['catsh_SubhaloVel']
        
#         self.use_cicw = 1 # this should always use CICW
#         return
#     # ['catgrp_GroupNsubs', 'catgrp_Group_M_Crit200', 'catgrp_id', 'catgrp_is_primary', 'catsh_gr_normal',
#     #  'catsh_id', 'catxt_gr_dust', 'config', 'ptldm_Coordinates', 'ptldm_ParticleIDs', 'ptldm_Velocities',
#     #   'ptldm_first', 'ptldm_n', 'ptlgas_Coordinates', 'ptlgas_ParticleIDs', 'ptlgas_Velocities', 
#     #   'ptlgas_first', 'ptlgas_n', 'ptlstr_Coordinates', 'ptlstr_ParticleIDs', 'ptlstr_Velocities', 
#     #   'ptlstr_first', 'ptlstr_n']

    
#     def _loadSlices(self, fptl):
        
#         shslc = []
#         for i in range(len(fptl-1)):
#             shslc.append(slice(fptl[i],fptl[i+1]))
#         shslc.append(slice(fptl[-1], -1))
#         return shslc
    
#     def _useHydrotools(self, gd):
#         ht_suf = gd['ht_suf']

#         xtf = ['gr_dust']
#         shf = ['gr_normal', 'SubhaloPos', 'SubhaloVel', 'SubhaloMassType']
#         ptf = ['Coordinates', 'Velocities', 'ParticleIDs', 'Masses']
#         sim = self._get_simname_as_ht_input(self.simname)
#         if self.use_stmass:
#             iface_run.extractGalaxyData(sim=sim, snap_idx=self.snapshot, verbose = bool(self.v),
#                     file_suffix=ht_suf, output_compression='gzip', catxt_get=True, catxt_fields=xtf,
#                     catsh_get=True, catsh_fields=shf, ptlstr_get=True, ptlstr_fields=ptf,
#                     output_path=gd['results'], catgrp_get = False)
#         else:
#             iface_run.extractGalaxyData(sim=sim, snap_idx=self.snapshot, verbose = bool(self.v),
#                     file_suffix=ht_suf, output_compression='gzip', catxt_get=True, catxt_fields=xtf,
#                     catsh_get=True, catsh_fields=shf, ptlstr_get=True, ptlstr_fields=ptf,
#                     ptldm_get=True, ptldm_fields=ptf, ptlgas_get=True, ptlgas_fields=ptf,
#                     output_path=gd['results'], catgrp_get = False)
    
#         return
    
    
#     @staticmethod
#     def _get_simname_as_ht_input(simname):
#         # since ht uses different keywords for simnames, include this
#         # dictionary to traverse between the two
#         ht_sim = {'tng100':'tng75', 'tng300':'tng205', 'tng50':'tng35'}

#         return ht_sim[simname]
    
#     def _getMasks(self):
#         masks = []
#         resolved_mask = self.isResolved(self.mass, self.r, self.res_dict)
#         col_def = self.getColorDefinitions()[self.col]
#         for g in self.gridnames:
#             if 'dust' in g:
#                 gr = self.gr_dust
#             else:
#                 gr = self.gr
            
#             if 'red' in g:
#                 mask = self.isRed(gr, self.mass, col_def)
#             else:
#                 mask = np.invert(self.isRed(gr, self.mass, col_def))
            
#             mask *= resolved_mask
#             masks.append(mask)
            

#         return masks
    
#     def computeGrids(self):
#         # figure out which subhalos are red/blue
#         # need to do this first to avoid having multiple grid arrays which take a lot of memory
#         masks = self._getMasks()
#         ht = self.ht_file
#         # iterate over each grid, use the mask to figure out
#         # which data that you want to add to the grid 
#         for i in range(len(self.gridnames)):
#             mask = masks[i]
#             gn = self.gridnames[i]
            
#             self.grid = Grid(gn, self.resolution)
#             # mask off the subhalos not included in this color definition
#             shpos = self.pos[mask, :]
#             # for each particle type
#             for p in self.ptl_names:
#                 # load the data for this particle type
#                 ptlpos = ht['%s_Coordinates'%p]
#                 ptlmass = ht['%s_Masses'%p]

#                 ptlslc = self._loadSlices(ht['%s_first'])
#                 # iterate over each subhalo, placing the particles into the grid
#                 for s in range(len(shpos)):
#                     # the positions are relative to the subhalos position
#                     pos_for_grid = ptlpos[ptlslc[s], :] + shpos[s, :]
#                     mass_for_grid = ptlmass[ptlslc[s]]
#                     self.grid.CICW(pos_for_grid, self.header['BoxSize'], mass_for_grid)
#             self.saveData(gn)
                
        
#         # now do the same in redshift space
#         for i in range(len(self.gridnames)):
#             mask = masks[i]
#             gn = self.gridnames[i]
            
#             self.grid = Grid(gn, self.resolution)
#             self.grid.toRSS()
#             # mask off the subhalos not included in this color definition
#             shpos = self.pos[mask, :]
#             shvel = self.vel[mask, :]
#             # for each particle type
#             for p in self.ptl_names:
#                 # load the data for this particle type
#                 ptlpos = ht['%s_Coordinates'%p]
#                 ptlmass = ht['%s_Masses'%p]
#                 ptlvel = ht['%s_Velocities'%p]

#                 ptlslc = self._loadSlices(ht['%s_first'])
#                 # iterate over each subhalo, placing the particles into the grid
#                 for s in range(len(shpos)):
#                     # the positions are relative to the subhalos position
#                     pos_for_grid = ptlpos[ptlslc[s], :] + shpos[s, :]
#                     vel_for_grid = ptlvel[ptlslc[s], :] + shvel[s, :]
#                     mass_for_grid = ptlmass[ptlslc[s]]
#                     self._toRedshiftSpace(pos_for_grid, vel_for_grid)
#                     self.grid.CICW(pos_for_grid, self.header['BoxSize'], mass_for_grid)
#             self.saveData(gn)
#         return

#     def saveData(self, gridname):
#         dat = super().saveData(self.col)
#         dct = dat.attrs
#         dct['use_res'] = self.use_res
#         dct['is_stmass'] = self.use_stmass
#         if 'dust' in gridname:
#             dct['used_dust'] = True
#         else:
#             dct['used_dust'] = False
#         dct['is_massden'] = 1
#         return 
