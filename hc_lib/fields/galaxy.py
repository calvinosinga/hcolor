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
            pkl_path, verbose, catshpath, fieldname='galaxy', runtype=''):
        

        self.fieldname = fieldname
        self.runtype = runtype
        self.loadpath = catshpath
        super().__init__(simname, snapshot, axis, resolution, pkl_path, verbose)
        if verbose:
            print('RUNTYPE: ' + runtype)
        return

    def getGridProps(self):
        gridnames = {}
        runtype = self.runtype
        def _addGrids(colors, resolutions, colordefs, MAS_type, spaces, mass_type, censat):
            for c in colors:
                for r in resolutions:
                    for cd in colordefs:
                        for MT in MAS_type:
                            for mt in mass_type:
                                for s in spaces:
                                    for cs in censat:
                                        gp = galaxy_grid_props(MT, self.fieldname,
                                            s, c, mt, r, cd, cs)
                                        gridnames[gp.getH5DsetName()] = gp

        def _getCut():
            if self.snapshot == 67:
                return ['0.55']
            elif self.snapshot == 50:
                return ['0.5']
            else:
                return ['0.60']

        if runtype == 'fiducial':
            colors = ['blue', 'red']
            censat = ['both']
            resolutions = ['diemer']
            colordefs = _getCut()
            MAS_type = ['CICW']
            spaces = ['real', 'redshift']
            mass_type = ['stmass']

            _addGrids(colors, resolutions, colordefs, MAS_type, spaces, mass_type, censat)
            colors = ['resolved']
            colordefs = ['None']
            _addGrids(colors, resolutions, colordefs, MAS_type, spaces, mass_type, censat)
        
        elif runtype == 'alt_MAS':
            colors = ['blue', 'red']
            censat = ['both']
            resolutions = ['diemer']
            colordefs = _getCut()
            MAS_type = ['rCICW', 'CIC']
            spaces = ['real', 'redshift']
            mass_type = ['stmass']
            _addGrids(colors, resolutions, colordefs, MAS_type, spaces, mass_type, censat)
            colors = ['resolved']
            colordefs = ['None']
            _addGrids(colors, resolutions, colordefs, MAS_type, spaces, mass_type, censat)
        
        elif runtype == 'axis_test':
            colors = ['blue', 'red']
            censat = ['both']
            resolutions = ['diemer']
            colordefs = _getCut()
            MAS_type = ['CICW']
            spaces = ['redshift']
            mass_type = ['stmass']
            _addGrids(colors, resolutions, colordefs, MAS_type, spaces, mass_type, censat)
            colors = ['resolved']
            colordefs = ['None']
            _addGrids(colors, resolutions, colordefs, MAS_type, spaces, mass_type, censat)
        
        elif runtype == 'colordef_test':
            colors = ['blue', 'red']
            censat = ['both']
            resolutions = ['diemer']
            colordefs = galaxyColorDefs()
            spaces = ['real']
            mass_type = ['stmass']
            MAS_type = ['CICW']
            _addGrids(colors, resolutions, colordefs, MAS_type, spaces, mass_type, censat)

        elif runtype == 'bins_thresholds':
            colors = ['blue', 'red']
            censat = ['both', 'centrals', 'satellites']
            resolutions = []
            for r in list(galaxyResDefs(self.simname).keys()):
                if 'bin' in r or 'threshold' in r:
                    resolutions.append(r)
            if self.simname == 'tng100':
                resolutions.append('tng100-2')
                resolutions.append('tng300')
            colordefs = _getCut()
            MAS_type = ['CICW']
            spaces = ['real', 'redshift']
            mass_type = ['stmass']
            _addGrids(colors, resolutions, colordefs, MAS_type, spaces, mass_type, censat)
            colors = ['resolved']
            colordefs = ['None']
            _addGrids(colors, resolutions, colordefs, MAS_type, spaces, mass_type, censat)            

        elif runtype == 'species_test':
            colors = ['blue', 'red']
            resolutions = ['diemer']
            censat = ['both']
            colordefs = _getCut()
            MAS_type = ['CICW']
            spaces = ['real', 'redshift']
            mass_type = ['stmass', 'total']
            _addGrids(colors, resolutions, colordefs, MAS_type, spaces, mass_type, censat)
            colors = ['resolved']
            colordefs = ['None']
            _addGrids(colors, resolutions, colordefs, MAS_type, spaces, mass_type, censat)
        
        elif runtype == 'all_test':
            colordefs = ['None']
            censat = ['both']
            MAS_type = ['CICW']
            spaces = ['real', 'redshift']
            mass_type = ['total', 'stmass']
            colors = ['all']
            resolutions = ['None']
            _addGrids(colors, resolutions, colordefs, MAS_type, spaces, mass_type, censat)
        
        elif runtype == 'centrals_test':
            colordefs = _getCut()
            colors = ['blue', 'red']
            censat = ['centrals', 'satellites', 'both']
            MAS_type = ['CICW']
            spaces = ['real', 'redshift']
            mass_type = ['stmass']
            resolutions = ['diemer']
            _addGrids(colors, resolutions, colordefs, MAS_type, spaces, mass_type, censat)
            colors = ['resolved']
            colordefs = ['None']
            _addGrids(colors, resolutions, colordefs, MAS_type, spaces, mass_type, censat)
        return gridnames
    
    
    def makeSlice(self, grid, grid_props, perc=0.1, mid=None):
        return super().makeSlice(grid, grid_props, perc=perc, mid=mid)
    
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
            
            grid.runMAS(gc.props['mas'], pos, self.header['BoxSize'], mass)
            
            return grid
        ###########################################################################

        # saves the associated pickle filepath to the hdf5 output
        super().setupGrids(outfile)

        # getting the galaxy data
        fields = ['SubhaloStellarPhotometrics','SubhaloPos','SubhaloMassType',
                'SubhaloVel']   
        pos, vel, mass, photo = self._loadGalaxyData(self.loadpath, fields)
        centrals = self._loadGroupData(self.loadpath, ['GroupFirstSub'])
        temp = copy.copy(pos)
        rspos = self._toRedshiftSpace(temp, vel)
        del vel, temp
        
        
        for g in self.gridprops.values():
            if self.v:
                print("now making grids for %s"%g.getH5DsetName())

            # create the appropriate mask for the color
            gp = g.props
            if not gp['gal_res'] is 'None':
                resolved_dict = galaxyResDefs(self.simname)[gp['gal_res']]
                resolved_mask = galaxyResolvedMask(mass[:, 4], mass[:, 0], photo, resolved_dict)
            else: # "all" does not have resdef -> so none are masked
                resolved_mask = np.ones_like(mass[:, 4], dtype=bool)
            
            
            if gp['censat'] == 'centrals':
                censat_mask = np.zeros_like(resolved_mask, dtype = bool)
                censat_mask[centrals[centrals >= 0]] = True
            elif gp['censat'] == 'satellites':
                censat_mask = np.ones_like(resolved_mask, dtype = bool)
                censat_mask[centrals[centrals >= 0]] = False
            else:
                censat_mask = np.ones_like(resolved_mask, dtype = bool)

            resolved_mask = resolved_mask & censat_mask

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

            if gp['gal_species'] == 'stmass':
                grid = computeGal(pos_arr[mask, :], mass[mask, 4], g)
            else:
                total_mass = np.sum(mass, axis = 1)
                grid = computeGal(pos_arr[mask, :], total_mass[mask], g)



            # commenting out because comparisons to Papastergis will be difficult
            # if gp['gal_res'] not in self.gir_hists.keys() and gp['gal_res'] == 'papastergis_SDSS':
            #     gir = self.make_gi_r(photo['gi'][resolved_mask], photo['r'][resolved_mask])
            #     self.gir_hists[gp['gal_res']] = gir
            
            # if gp['gal_res'] not in self.hists_done and not gp['gal_res'] is None:
            #     self.make_gr_stmass(g, photo['gr'][resolved_mask], mass[resolved_mask, 4])
            
            self.saveData(outfile, grid, g)
            del grid
        
        return
    
    def setupGrids(self, outfile):
        return super().setupGrids(outfile)
        
    def make_gr_stmass(self, grid_props, gr, stmass):
        gp = grid_props.props
        start = time.time()
        stmass = np.ma.masked_equal(stmass, 0)
        gr_stmass = np.histogram2d(np.log10(stmass), gr, bins=50)
        runtime = time.time() - start
        rc = ResultContainer(self, grid_props, runtime, gr_stmass[1],
                    yvalues=gr_stmass[2], zvalues=gr_stmass[0])
        self.hists.append(rc)
        self.hists_done.append(gp['gal_res'])
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
            catshpath, dustpath, runtype = 'fiducial'):
        super().__init__(simname, snapshot, axis, resolution, 
                pkl_path, verbose, catshpath, 'galaxy_dust', runtype)
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
    

