#!/usr/bin/env python3
"""

"""
from hc_lib.grid.grid import Grid
from hc_lib.fields.field_super import Field, grid_props
from hc_lib.build.input import Input
import h5py as hp
import numpy as np

class galaxy_grid_props(grid_props):
    """
    Since each galaxy field has an enormous number of grids, this contains the data
    for one grid
    """
    def __init__(self, color, mas, field, mass_type, resdef, coldef):
        other = {}
        lst = [color, mass_type, resdef, coldef]
        keys = ['color', 'mass', 'resdef','coldef']
        for i in range(len(lst)):
            other[keys[i]] = lst[i]

        super().__init__(color, mas, field, other)

        return
    
    def isCompatible(self, other):
        op = other.props
        sp = self.props

        # for galaxyXgalaxy
        if op['field'] == sp['field']:
            mas_match = op['mas'] == sp['mas']
            stmass_or_total = op['mass'] == sp['mass']
            resdef_match = op['resdef'] == sp['resdef'] and op['resdef'] == 'diemer'
            coldef_match = op['coldef'] == sp['coldef'] and sp['coldef'] == '0.6'
            
            return mas_match and stmass_or_total and resdef_match and coldef_match
        
        # hiptlXgalaxy handled by hiptl
        
        # hisubhaloXgalaxy handled by hisubhalo

        # vnXgalaxy handled by vn

        return True

    def isIncluded(self):

        def test(cds, mts, schts):
            cdtest = self.props['coldef'] in cds
            mtest = self.props['mass'] in mts
            mastest = self.props['mas'] in schts
            return cdtest and mtest and mastest
        
        if self.props['resdef'] == 'papa':
            cds = ['papa']
            ms = ['stmass']
            schts = ['CIC']
            return test(cds, ms, schts)
        
        elif self.props['resdef'] == 'wiggleZ':
            return False # not implemented
        
        elif self.props['resdef'] == 'eBOSS':
            cds = ['eBOSS']
            ms = ['stmass']
            schts = ['CIC']
            return False


        elif self.props['resdef'] == '2df':
            return False # not implemented

        # everything that isn't a color definition associated with an observation is fine
        elif self.props['resdef'] == 'diemer':
            coldef_is_compatible = not (self.props['coldef'] == 'papa' or self.props['coldef'] == 'eBOSS')
            # CIC between stmass and all mass should be the same - removing redundancy
            is_CICW = self.props['mas'] == 'CICW'
            is_CIC_and_stmass = self.props['mas'] == 'CIC' and self.props['mass'] == 'stmass'

            return coldef_is_compatible and (is_CICW or is_CIC_and_stmass)

        # if this is gridprop obj for resolved, then
        elif self.color == 'resolved':
            return True
        
        elif self.color == 'all':
            return True
        return False


    


class galaxy(Field):

    def __init__(self, simname, snapshot, axis, resolution, 
            pkl_path, verbose, catshpath, fieldname='galaxy'):
        

        self.fieldname = fieldname
        # we use blue/red/all for every color definition

        # each run will do each color definition provided, but will need a different run to
        # use a different resolution definition.
        
        self.isHI = False

        self.loadpath = catshpath
        self.counts = {}
        self.grsm_hists = {}
        self.gir_hists = {}

        super().__init__(simname, snapshot, axis, resolution, pkl_path, verbose)
        return
    
    def getGridProps(self):
        colors = ['blue', 'red']
        resolutions = list(self.getResolutionDefinitions(self.simname).keys())
        colordefs = self.getColorDefinitions()
        mass_type = ['stmass', 'total']
        MAS_type = ['CIC','CICW']
        gridnames = {}

        for c in colors:
            for r in resolutions:
                for cd in colordefs:
                    for mt in mass_type:
                        for Mt in MAS_type:
                            gp = galaxy_grid_props(c, Mt, self.fieldname, mt, r, cd)
                            if gp.isIncluded():
                                gridnames[gp.getName()] = gp
        for r in resolutions:
            for mt in mass_type:
                for Mt in MAS_type:
                    gp = galaxy_grid_props('resolved', Mt, self.fieldname, mt, r, None)
                    if gp.isIncluded():
                        gridnames[gp.getName()] = gp
        for mt in mass_type:
            for Mt in MAS_type:
                gp = galaxy_grid_props('all', Mt, self.fieldname, mt, None, None)
                if gp.isIncluded():
                    gridnames[gp.getName()] = gp
        
        return gridnames
    
    @staticmethod
    def colorIndices(photo, stmass, col_def):
        if col_def == 'nelson':
            x = stmass
            y = photo['gr']
            red_mask = y > 0.65 + 0.02 * (np.log10(x) - 10.28)
            blue_mask = np.invert(red_mask)
        elif col_def == 'papa':
            x = photo['r']
            y = photo['gi']
            red_mask = y > 0.0571 * (x + 24) + 1.25
            blue_mask = y < 0.0571 * (x + 24) + 1.1
        elif col_def == 'eBOSS':
            #TODO: still need to implement without LRG ELG separate
            blue_mask = np.ones_like(stmass)
            red_mask = np.zeros_like(stmass)
        else:
            y = photo['gr']
            x = float(col_def)
            red_mask = y > x
            blue_mask = np.invert(red_mask)
        return blue_mask, red_mask
        
    
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
    
    @classmethod
    def getResolutionDefinitions(cls, simname):
        # taken from Pillepich et al 2018, table 1 (in solar masses)
        mean_baryon_cell = {'tng100':1.4e6, 'tng100-2':11.2e6, 'tng100-3':89.2e6,
                'tng300':11e6, 'tng300-2':88e6, 'tng300-3':703e6}
        # papastergis: z=.0023-0.05
        # wolz: z=0.6-1.0
        # anderson: z ~ 0

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
        galaxy_min_resolution['wiggleZ'] = {'r':(20,22)}
        
        # eBOSS Emission line galaxies
        galaxy_min_resolution['eBOSS'] = {'g':(21.825,22.825), 'gr':'gr_elg', 
                'rz':'rz_elg'}
        # since gr and rz depend on other values, use strings to indicate a method
        # to use in the resolution definition

        # galaxy_min_resolution['eBOSS_LRG'] = {'i':(19.9,21.8), 'z':(-np.inf, 19.95),
        #         'ri':(0.98, np.inf)}
        # I still need to check if there is an equivalent band for IRACI in TNG

        galaxy_min_resolution['2df'] = {'bj':(19.45)}
        return galaxy_min_resolution
    
    @classmethod
    def getColorDefinitions(cls):

        implemented_color_defs = ['papa', 'nelson', '0.50', '0.55', '0.60', '0.65', '0.70', 'eBOSS']
        
        return implemented_color_defs
    
    
    
    def _loadGalaxyData(self, simpath, fields):
        data = super()._loadGalaxyData(simpath, fields)
        pos = data['SubhaloPos'][:]
        vel = data['SubhaloVel'][:]

        photo = data['SubhaloStellarPhotometrics'][:]
        mass = data['SubhaloMassType'][:]

        photo_dict = {}
        photo_dict['gr'] = photo[:, 4] - photo[:, 5]
        photo_dict['r'] = photo[:, 5]
        photo_dict['i'] = photo[:, 6]
        photo_dict['z'] = photo[:, 7]
        photo_dict['g'] = photo[:, 4]
        photo_dict['ri'] = photo_dict['r'] - photo_dict['i']
        photo_dict['rz'] = photo_dict['r'] - photo_dict['z']
        photo_dict['gi'] = photo_dict['g'] - photo_dict['i']
        mass = self._convertMass(mass)
        pos = self._convertPos(pos)
        vel = self._convertVel(vel)
        return pos, vel, mass, photo_dict

    def computeGrids(self, outfile):
        ########################## HELPER FUNCTION ###############################
        def computeGal(pos, mass, gc, is_in_rss):
            grid = Grid(gc.getName(), self.resolution, verbose=self.v)
            if is_in_rss:
                grid.toRSS()

            if gc.props['mas'] == 'CICW':
                grid.CICW(pos, self.header['BoxSize'], mass)
            else:
                grid.CIC(pos, self.header['BoxSize'])
            
            return grid
        ###########################################################################

        # saves the associated pickle filepath to the hdf5 output
        super().computeGrids(outfile)

        # getting the galaxy data
        fields = ['SubhaloStellarPhotometrics','SubhaloPos','SubhaloMassType',
                'SubhaloVel']   
        pos, vel, mass, photo = self._loadGalaxyData(self.loadpath, fields)
        
            
        in_rss = False
        for g in self.gridprops.values():
            if self.v:
                print("now making grids for %s"%g.getName())

            # create the appropriate mask for the color
            gp = g.props
            if not gp['resdef'] is None:
                resolved_dict = self.getResolutionDefinitions(self.simname)[gp['resdef']]
                resolved_mask = self.isResolved(mass[:, 4], photo, resolved_dict)
            else: # "all" does not have resdef -> so none are masked
                resolved_mask = np.ones_like(mass[:, 4], dtype=bool)
            

            if gp['color'] == 'red':
                blue_mask, red_mask = self.colorIndices(photo, mass[:, 4], gp['coldef'])
                mask = red_mask * resolved_mask
            elif gp['color'] == 'blue':
                blue_mask, red_mask = self.colorIndices(photo, mass[:, 4], gp['coldef'])
                mask = blue_mask * resolved_mask
            elif gp['color'] == 'resolved':
                mask = resolved_mask
            elif gp['color'] == 'all':
                mask = np.ones_like(resolved_mask, dtype=bool)
            
            # count the number of galaxies used for this grid
            self.counts[g.getName()] = np.sum(mask)
            if gp['mass'] == 'stmass':
                grid = computeGal(pos[mask, :], mass[mask, 4], g, in_rss)
            else:
                total_mass = np.sum(mass, axis = 1)
                grid = computeGal(pos[mask, :], total_mass[mask], g, in_rss)

            if gp['resdef'] not in self.gir_hists.keys() and gp['resdef'] == 'papa':
                gir = self.make_gi_r(photo['gi'][resolved_mask], photo['r'][resolved_mask])
                self.gir_hists[gp['resdef']] = gir
            
            if gp['resdef'] not in self.grsm_hists.keys() and not gp['resdef'] is None:
                grsm = self.make_gr_stmass(photo['gr'][resolved_mask], mass[resolved_mask, 4])
                self.grsm_hists[gp['resdef']] = grsm
            
            self.saveData(outfile, grid, g)
            del grid
        
        # now doing redshift-space grids
        pos = self._toRedshiftSpace(pos, vel)
        in_rss = True

        for g in list(self.gridprops.values()):
            if self.v:
                print("now making grids for %s"%g.getName())

            # create the appropriate mask for the color
            gp = g.props

            if not gp['resdef'] is None:
                resolved_dict = self.getResolutionDefinitions(self.simname)[gp['resdef']]
                resolved_mask = self.isResolved(mass[:, 4], photo, resolved_dict)
            else:
                resolved_mask = np.ones_like(mass[:, 4], dtype=bool)
            
            if gp['color'] == 'red':
                blue_mask, red_mask = self.colorIndices(photo, mass[:, 4], gp['coldef'])
                mask = red_mask * resolved_mask
            elif gp['color'] == 'blue':
                blue_mask, red_mask = self.colorIndices(photo, mass[:, 4], gp['coldef'])
                mask = blue_mask * resolved_mask
            elif gp['color'] == 'resolved':
                mask = resolved_mask
            elif gp['color'] == 'all':
                mask = np.ones_like(resolved_mask, dtype=bool)
            

            if gp['mass'] == 'stmass':
                grid = computeGal(pos[mask, :], mass[mask, 4], g, in_rss)
            else:
                total_mass = np.sum(mass, axis = 1)
                grid = computeGal(pos[mask, :], total_mass[mask], g, in_rss)
            self.saveData(outfile, grid, g)
            del grid
        
        return
    
    def make_gr_stmass(self, gr, stmass):
        stmass = np.ma.masked_equal(stmass, 0)
        gr_stmass = np.histogram2d(np.log10(stmass), gr, bins=50)
        return gr_stmass
    
    def make_gi_r(self, gi, r):
        gi_r = np.histogram2d(r, gi, bins=50)
        return gi_r
    
    def _convertVel(self, vel):
        # subhalos' velocities are already in km/s
        return vel
    
    def saveData(self, outfile, grid, gp):
        dat = super().saveData(outfile, grid, gp)
        dat.attrs['used_dust'] = False
        return dat

    
    

    

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
        photo_dict['g'] = photo[:, 1, minidx]
        photo_dict['ri'] = photo_dict['r'] - photo_dict['i']
        photo_dict['rz'] = photo_dict['r'] - photo_dict['z']
        photo_dict['gi'] = photo_dict['g'] - photo_dict['i']
        dustfile.close()
        return pos, vel, mass, photo_dict
        

    def saveData(self, outfile, grid, gp):
        dat = super().saveData(outfile, grid, gp)
        print('galaxy_dust\'s saveData finished calling galaxy')
        # dct = dat.attrs
        # dct['used_dust'] = True
        return dat
    

