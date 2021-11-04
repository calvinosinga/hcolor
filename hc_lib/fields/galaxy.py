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
        self.color = color
        lst = [mass_type, resdef, coldef]
        keys = ['mass', 'resdef','coldef']
        for i in range(len(lst)):
            other[keys[i]] = lst[i]

        super().__init__(color, mas, field, other)

        return
    
    
    # def isCompatible(self, other):
    #     # def testProps(tests):
    #     #     results = np.zeros(len(tests))
    #     #     for t in range(len(tests)):
    #     #         results[t] = op[tests[t]] == sp[tests[t]]
            
    #     #     return results.all()
        
    #     # op = other.props
    #     # sp = self.props


    #     # if sp['field'] == op['field']:
    #     #     tests = ['resdef', 'coldef', 'mas', 'mass']
    #     #     return testProps(tests)
        
    #     # elif sp['resdef'] == 'papa':
    #     #     if op['field'] == 'hisubhalo':
    #     #         tests = ['resdef', 'mas']
    #     #         return testProps(tests)
        

    #     # elif sp['resdef'] == 'eBOSS':
    #     #     if op['field'] == 'hiptl' or op['field'] == 'vn':
    #     #         return op['mass'] == 'temp'
        

    #     # elif sp['resdef'] == 'wiggleZ':
    #     #     if op['field'] == 'hiptl' or op['field'] == 'vn':
    #     #         return op['mass'] == 'temp'
                

    #     # elif sp['resdef'] == '2df':
    #     #     if op['field'] == 'hiptl' or op['field'] == 'vn':
    #     #         return op['mass'] == 'temp'
                


    #     # elif sp['resdef'] == 'diemer':
    #     #     fiducial_cd = ['nelson','0.6','0.55', '0.65']
    #     #     return sp['coldef'] in fiducial_cd
            
    #     return True

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
        
        elif self.props['resdef'] == 'wigglez':
            return False # not implemented
        
        elif self.props['resdef'] == 'eBOSS':
            cds = ['eBOSS']
            ms = ['stmass']
            schts = ['CIC']
            return False


        elif self.props['resdef'] == '2df':
            return False # not implemented

        elif self.props['resdef'] == 'diemer':
            cds = galaxy.getColorDefinitions()
            cds.remove('papa')
            cds.remove('eBOSS')
            ms = ['stmass','mass']
            schts = ['CIC', 'CICW']
            return test(cds, ms, schts)

        return False


    


class galaxy(Field):

    def __init__(self, simname, snapshot, axis, resolution, 
            pkl_path, verbose, catshpath, fieldname='galaxy'):
        
        super().__init__(simname, snapshot, axis, resolution, pkl_path, verbose)

        self.fieldname = fieldname
        # we use blue/red/all for every color definition

        # each run will do each color definition provided, but will need a different run to
        # use a different resolution definition.
        
        self.isHI = False

        self.loadpath = catshpath
        self.counts = {}
        self.grsm_hists = {}
        self.gir_hists = {}

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

        implemented_color_defs = ['papa', 'nelson', '0.5', '0.55', '0.6', '0.65', '0.7', 'eBOSS']
        
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
            resolved_dict = self.getResolutionDefinitions(self.simname)[gp['resdef']]

            resolved_mask = self.isResolved(mass[:, 4], photo, resolved_dict)
            if g.color == 'red':
                blue_mask, red_mask = self.colorIndices(photo, mass[:, 4], gp['coldef'])
                mask = red_mask * resolved_mask
            elif g.color == 'blue':
                blue_mask, red_mask = self.colorIndices(photo, mass[:, 4], gp['coldef'])
                mask = blue_mask * resolved_mask
            elif g.color == 'resolved':
                mask = resolved_mask
            elif g.color == 'all':
                mask = np.ones_like(resolved_mask)
            
            # count the number of galaxies used for this grid
            self.counts[g.getName()] = np.sum(mask)
            if gp['mass'] == 'stmass':
                grid = computeGal(pos[mask, :], mass[mask, 4], g, in_rss)
            else:
                mass = np.sum(mass, axis = 1)
                grid = computeGal(pos[mask, :], mass[mask], g, in_rss)

            if gp['resdef'] not in self.gir_hists.keys() and gp['resdef'] == 'papa':
                gir = self.make_gi_r(photo['gi'][resolved_mask], photo['r'][resolved_mask])
                self.gir_hists[gp['resdef']] = gir
            
            if gp['resdef'] not in self.grsm_hists.keys():
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
            resolved_dict = self.getResolutionDefinitions(self.simname)[gp['resdef']]

            resolved_mask = self.isResolved(mass[:, 4], photo, resolved_dict)
            if g.color == 'red':
                blue_mask, red_mask = self.colorIndices(photo, mass[:, 4], gp['coldef'])
                mask = red_mask * resolved_mask
            elif g.color == 'blue':
                blue_mask, red_mask = self.colorIndices(photo, mass[:, 4], gp['coldef'])
                mask = blue_mask * resolved_mask
            elif g.color == 'resolved':
                mask = resolved_mask
            elif g.color == 'all':
                mask = np.ones_like(resolved_mask)
            

            if gp['mass'] == 'stmass':
                grid = computeGal(pos[mask, :], mass[mask, 4], g, in_rss)
            else:
                mass = np.sum(mass, axis = 1)
                grid = computeGal(pos[mask, :], mass[mask], g, in_rss)
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
        dct = dat.attrs
        dct['used_dust'] = True
        return dat
    

