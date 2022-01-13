#!/usr/bin/env python3
"""

"""
from hc_lib.grid.grid import Grid
from hc_lib.grid.grid_props import galaxy_grid_props
from hc_lib.fields.field_super import Field
from hc_lib.fields.run_lib import galaxyColorDefs
from hc_lib.fields.run_lib import galaxyResDefs
from hc_lib.fields.run_lib import galaxyColorMasks
from hc_lib.fields.run_lib import galaxyResolvedMask
from hc_lib.fields.field_super import ResultContainer
import time
import h5py as hp
import numpy as np
import copy


class galaxy(Field):

    def __init__(self, simname, snapshot, axis, resolution, 
            pkl_path, verbose, catshpath, fieldname='galaxy'):
        

        self.fieldname = fieldname
        # we use blue/red/all for every color definition

        # each run will do each color definition provided, but will need a different run to
        # use a different resolution definition.
        
        self.loadpath = catshpath
        self.hists = []
        self.hists_done = []

        super().__init__(simname, snapshot, axis, resolution, pkl_path, verbose)
        return
    
    def getGridProps(self):
        colors = ['blue', 'red']
        #resolutions = list(galaxyResDefs(self.simname).keys())
        resolutions = ['diemer']
        colordefs = galaxyColorDefs()
        mass_type = ['stmass', 'total']
        # MAS_type = ['CIC','CICW']
        MAS_type = ['CICW']
        spaces = ['redshift', 'real']
        gridnames = {}

        for c in colors:
            for r in resolutions:
                for cd in colordefs:
                    for mt in mass_type:
                        for Mt in MAS_type:
                            for s in spaces:
                                gp = galaxy_grid_props(Mt, self.fieldname, s, c, mt, r, cd)
                                if gp.isIncluded():
                                    gridnames[gp.getH5DsetName()] = gp
        for r in resolutions:
            for mt in mass_type:
                for Mt in MAS_type:
                    for s in spaces:
                        gp = galaxy_grid_props(Mt, self.fieldname, s, 'resolved', mt, r, None)
                        if gp.isIncluded():
                            gridnames[gp.getH5DsetName()] = gp
        for mt in mass_type:
            for Mt in MAS_type:
                for s in spaces:
                    gp = galaxy_grid_props(Mt, self.fieldname,s, 'all', mt, None, None)
                    if gp.isIncluded():
                        gridnames[gp.getH5DsetName()] = gp
        
        return gridnames
    
    
    def makeSlice(self, grid, grid_props, perc=0.1, mid=None, avg=True):
        return super().makeSlice(grid, grid_props, perc=perc, mid=mid, avg=avg)
    
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

        # these conversions are from Y. Xu et al. 2007
        photo_dict['b_j'] = 0.15 + 0.13 * photo_dict['gr']
        photo_dict['r_f'] = photo_dict['r'] - 0.13

        mass = self._convertMass(mass)
        pos = self._convertPos(pos)
        vel = self._convertVel(vel)
        return pos, vel, mass, photo_dict

    def computeGrids(self, outfile):
        ########################## HELPER FUNCTION ###############################
        def computeGal(pos, mass, gc):
            grid = Grid(gc.getH5DsetName(), self.grid_resolution, verbose=self.v)
            
            if gc.props['mas'] == 'CICW':
                grid.CICW(pos, self.header['BoxSize'], mass)
            else:
                grid.CIC(pos, self.header['BoxSize'])
            
            return grid
        ###########################################################################

        # saves the associated pickle filepath to the hdf5 output
        super().setupGrids(outfile)

        # getting the galaxy data
        fields = ['SubhaloStellarPhotometrics','SubhaloPos','SubhaloMassType',
                'SubhaloVel']   
        pos, vel, mass, photo = self._loadGalaxyData(self.loadpath, fields)
        temp = copy.copy(pos)
        rspos = self._toRedshiftSpace(temp, vel)
        del vel, temp
        
        
        for g in self.gridprops.values():
            if self.v:
                print("now making grids for %s"%g.getH5DsetName())

            # create the appropriate mask for the color
            gp = g.props
            if not gp['gal_res'] is None:
                resolved_dict = galaxyResDefs(self.simname)[gp['gal_res']]
                resolved_mask = galaxyResolvedMask(mass[:, 4], photo, resolved_dict)
            else: # "all" does not have resdef -> so none are masked
                resolved_mask = np.ones_like(mass[:, 4], dtype=bool)
            

            if gp['color'] == 'red':
                blue_mask, red_mask = galaxyColorMasks(photo, mass[:, 4], gp['color_cut'])
                mask = red_mask * resolved_mask
            elif gp['color'] == 'blue':
                blue_mask, red_mask = galaxyColorMasks(photo, mass[:, 4], gp['color_cut'])
                mask = blue_mask * resolved_mask
            elif gp['color'] == 'resolved':
                mask = resolved_mask
            elif gp['color'] == 'all':
                mask = np.ones_like(resolved_mask, dtype=bool)
            
            mask.astype(bool)
            # count the number of galaxies used for this grid
            if gp['space'] == 'real':
                pos_arr = pos
            elif gp['space'] == 'redshift':
                pos_arr = rspos

            if gp['species'] == 'stmass':
                grid = computeGal(pos_arr[mask, :], mass[mask, 4], g)
            else:
                total_mass = np.sum(mass, axis = 1)
                grid = computeGal(pos_arr[mask, :], total_mass[mask], g)

            # commenting out because comparisons to Papastergis will be difficult
            # if gp['gal_res'] not in self.gir_hists.keys() and gp['gal_res'] == 'papastergis_SDSS':
            #     gir = self.make_gi_r(photo['gi'][resolved_mask], photo['r'][resolved_mask])
            #     self.gir_hists[gp['gal_res']] = gir
            
            if gp['gal_res'] not in self.hists_done and not gp['gal_res'] is None:
                self.make_gr_stmass(photo['gr'][resolved_mask], mass[resolved_mask, 4])
            
            self.saveData(outfile, grid, g)
            del grid
        
        return
    
    def setupGrids(self, outfile):
        return super().setupGrids(outfile)
        
    def make_gr_stmass(self, grid_props, gr, stmass):
        start = time.time()
        stmass = np.ma.masked_equal(stmass, 0)
        gr_stmass = np.histogram2d(np.log10(stmass), gr, bins=50)
        runtime = time.time() - start
        rc = ResultContainer(self, grid_props, runtime, gr_stmass[1],
                    yvalues=gr_stmass[2], zvalues=gr_stmass[0])
        self.hists.append(rc)
        self.hists_done.append(grid_props['gal_res'])
        return
    
    def make_gi_r(self, gi, r):
        gi_r = np.histogram2d(r, gi, bins=50)
        return gi_r
    
    def _convertVel(self, vel):
        # subhalos' velocities are already in km/s
        return vel
    
    def saveData(self, outfile, grid, gp):
        dat = super().saveData(outfile, grid, gp)
        return dat

    
    
################################################################################################
    

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

        # these conversions are from Y. Xu et al. 2007
        photo_dict['b_j'] = 0.15 + 0.13 * photo_dict['gr']
        photo_dict['r_f'] = photo_dict['r'] - 0.13

        dustfile.close()
        return pos, vel, mass, photo_dict
        

    def saveData(self, outfile, grid, gp):
        dat = super().saveData(outfile, grid, gp)
        return dat
    

