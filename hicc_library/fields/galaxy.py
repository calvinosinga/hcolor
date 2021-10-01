#!/usr/bin/env python3
"""

"""

from hicc_library.grid.grid import Grid
from hicc_library.fields.field_super import Field
import h5py as hp
import numpy as np
from Pk_library import XPk, XXi

class galaxy(Field):

    def __init__(self, simname, snapshot, axis, resolution, 
            pkl_path, verbose, catshpath, fieldname='galaxy'):
        
        super().__init__(simname, snapshot, axis, resolution, pkl_path, verbose)

        self.fieldname = fieldname
        self.gridnames, self.ignore = self.getGridnames()
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
        self.counts = {}

        self.xxis = {}
        self.xpks = {}
        self.tdxpks = {}

        if self.v:
            print('%s class variables:'%self.fieldname)
            print('Resolution definition: %s'%self.use_res)
            print('Resolution dictionary: %s'%str(self.res_dict))
            print('Is it using CICW?: %d'%self.use_cicw)
            print('Is it using stellar mass?: %d'%self.use_stmass)
            print('Color definitions:')
            print(self.col_defs)
        return
    
    def getGridnames(self):
        gridnames = ['resolved', 'all']
        ignore = {} # which grids should not have xpk computed from them
        colors = ['blue', 'red']
        coldefs = list(self.getColorDefinitions().keys())
        for cdef in coldefs:
            for c in colors:
                gridnames.append(c+'_'+cdef)
                if cdef == '0.6' or cdef == 'nelson':
                    ignore[c+'_'+cdef] = 0
                else:
                    ignore[c+'_'+cdef] = 1
                
        return gridnames, ignore
    
    @staticmethod
    def isRed(gr, stmass, color_dict):
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
        galaxy_red_definition['0.5'] = {'b':0.5, 'm':0, 'mb':0}
        galaxy_red_definition['0.6'] = {'b':0.6, 'm':0, 'mb':0}
        # trying it with a straight gr cut as well
        galaxy_red_definition['0.55'] = {'b':0.55, 'm':0, 'mb':0}
        galaxy_red_definition['0.65'] = {'b':0.65, 'm':0, 'mb':0}
        galaxy_red_definition['0.7'] = {'b':0.7, 'm':0, 'mb':0}
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
            mass = data['SubhaloMassType'][:]

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
            
            if self.ignore[gridname]:
                grid.ignoreGrid()
            return grid
        ###########################################################################

        # saves the associated pickle filepath to the hdf5 output
        super().computeGrids(outfile)

        # getting the galaxy data
        fields = ['SubhaloStellarPhotometrics','SubhaloPos','SubhaloMassType',
                'SubhaloVel']   
        pos, vel, mass, photo = self._loadGalaxyData(self.loadpath, fields)
        gr = photo['gr']
        
        # resolution definitions use stmass not all of the mass
        if not self.use_stmass:
            stmass = mass[:,4]
            mass = np.sum(mass, axis = 1)
            
        else:
            stmass = mass

        resolved_mask = self.isResolved(stmass, photo, self.res_dict)
        in_rss = False
        for g in self.gridnames:
            if self.v:
                print("now making grids for %s"%g)
            # the gridname contains the color and the color definition
            splt = g.split('_',1)
            color = splt[0]
            # for 'resolved' + 'all' grids, they have no color definition
            # so the split will return a list of length one
            color_dict = None
            if len(splt) == 2:
                col_key = splt[1]
                color_dict = self.getColorDefinitions()[col_key]
            else:
                col_key = ''
            # create the appropriate mask for the color


            if color == 'red':
                mask = self.isRed(gr, stmass, color_dict)
                mask = mask * resolved_mask
            elif color == 'blue':
                mask = np.invert(self.isRed(gr, stmass, color_dict)) * resolved_mask
            elif color == 'resolved':
                mask = resolved_mask
            elif color == 'all':
                mask = np.ones_like(resolved_mask)
            
            # count the number of galaxies used for this grid
            self.counts[g] = np.sum(mask)
            grid = computeGal(pos[mask, :], mass[mask], g)
            self.saveData(outfile, grid, col_key)
            del grid
        
        # now doing redshift-space grids
        pos = self._toRedshiftSpace(pos, vel)
        in_rss = True

        for g in self.gridnames:
            # the gridname contains the color and the color definition
            splt = g.split('_',1)
            color = splt[0]
            # for 'resolved' + 'all' grids, they have no color definition
            # so the split will return a list of length one
            if len(splt) == 2:
                col_key = splt[1]
                color_dict = self.getColorDefinitions()[col_key]
            else:
                col_key = ''
            # create the appropriate mask for the color
            if color == 'red':
                mask = self.isRed(gr, mass, color_dict) * resolved_mask
            elif color == 'blue':
                mask = np.invert(self.isRed(gr, mass, color_dict)) * resolved_mask
            elif color == 'resolved':
                mask = resolved_mask
            elif color == 'all':
                mask = np.ones_like(resolved_mask)
            
            grid = computeGal(pos[mask, :], mass[mask], g)
            self.saveData(outfile, grid, col_key)
            del grid
        
        self.make_gr_stmass(gr[resolved_mask],stmass[resolved_mask])
        return
    
    def make_gr_stmass(self, gr, stmass):
        stmass = np.ma.masked_equal(stmass, 0)
        self.gr_stmass = np.histogram2d(np.log10(stmass), gr, bins=50)
        return
    
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
    

