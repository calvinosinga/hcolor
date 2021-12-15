"""

"""
import h5py as hp
import numpy as np
from hc_lib.fields.field_super import Field, grid_props
from hc_lib.grid.grid import Chunk
import copy
from hc_lib.fields.galaxy import galaxy
import scipy.constants as sc

class hiptl_grid_props(grid_props):

    def __init__(self, mas, field, space, model, mass_or_temp = None, nH = None):
        other = {}
        other['map'] = mass_or_temp
        other['model'] = model
        if not nH is None:
            self.nH_bin = nH
            nH_str = str(nH)
            other['nH_bin'] = nH_str
        else:
            other['nH_bin'] = nH
        super().__init__(mas, field, space, other)
        return
    
    def isCompatible(self, other):
        sp = self.props
        op = other.props

        # hiptl/h2ptlXgalaxy/galaxy_dust
        if 'galaxy' in op['fieldname']:
            # for comparisons to Anderson and Wolz -> stmass/resdef is eBOSS, wiggleZ, 2df
            if 'temp' == sp['map']:
                obs_defs = galaxy.getObservationalDefinitions()
                obs_defs.remove('papastergis_SDSS')
                match_obs = op['gal_res'] in obs_defs and op['color_cut'] in obs_defs
                return match_obs
            
            # if a mass map, it is either diemer
            elif op['gal_res'] == 'diemer':
                # the important color definitions
                cols = ['0.60', '0.55', '0.65', 'visual_inspection']

                # also include resolved
                is_resolved = op['color'] == 'resolved'

                return op['color_cut'] in cols or is_resolved
            
            # ignore all papa resdefs -> hisubhalo is more comparable
            elif op['gal_res'] == 'papa':
                return False
            
            # if all = color, then include
            elif op['color'] == 'all':
                return True

        # hiptlXptl
        else:
            # include if mass map, not temp map
            return sp['map'] == 'mass'
            

    
class hiptl(Field):

    def __init__(self, simname, snapshot, axis, resolution, chunk, pkl_path, 
                verbose, snappath, hih2filepath, fieldname = 'hiptl'):
        
        self.chunk = chunk

        self.fieldname = fieldname
        self.hih2filepath = hih2filepath%self.chunk
        self.loadpath = snappath%self.chunk

        super().__init__(simname, snapshot, axis, resolution, pkl_path, verbose)
        return
    
    def getGridProps(self):
        models = self.getMolFracModelsPtl()
        mass_or_temp = ['mass', 'temp']
        spaces = ['redshift', 'real']
        grp = {}
        for s in spaces:
            for m in models:
                for mt in mass_or_temp:
                    gp = hiptl_grid_props('CICW', self.fieldname, s, m, mass_or_temp = mt)
                    if gp.isIncluded():
                        grp[gp.getName()] = gp
        return grp
    
    @staticmethod
    def getMolFracModelsPtl():
        return ['GD14', 'GK11', 'S14', 'K13']
    
    def computeGrids(self, outfile):
        super().computeGrids(outfile)
        hih2file = hp.File(self.hih2filepath, 'r')
        pos, vel, mass, density = self._loadSnapshotData()
        temp = copy.copy(pos)
        rspos = self._toRedshiftSpace(temp, vel)
        del temp, vel

        ############ HELPER FUNCTION ############################################
        def computeHI(gprop, pos, mass, density):
            grid = Chunk(gprop.getName(), self.grid_resolution, self.chunk, verbose=self.v)
            
            if self.v:
                hs = '#' * 20
                print(hs+" COMPUTE HI FOR %s "%(gprop.getName().upper()) + hs)

            # getting data from hih2 files
            neutfrac = hih2file['PartType0']['f_neutral_H'][:]
            molfrac = hih2file['PartType0']['f_mol_'+gprop.model][:]
            
            # converting the masses to HI mass
            HImass = mass*(1-molfrac)*neutfrac
            HIrho = density * (1 - molfrac) * neutfrac

            # neutral fraction is -1 where models are not defined, 
            # so replace those values with 0
            HImass = np.where(HImass>=0, HImass, 
                    np.zeros(HImass.shape, dtype=np.float32))
            HIrho = np.where(HIrho >= 0, HIrho, np.zeros_like(HIrho))

   
            # place particles into grid
            if gprop.props["map"] == 'temp':
                T_HI = self.temperatureMap(HIrho)
                grid.CICW(pos, self.header['BoxSize'], T_HI)
            else:
                grid.CICW(pos, self.header['BoxSize'], HImass)

            # save them to file
            self.saveData(outfile, grid, gprop)
            # if we are in redshift space, the grid handles saving with 'rs'
            return
        #############################################################################

        for g in list(self.gridprops.values()):
            if g.props['space'] == 'real':
                pos_arr = pos
            elif g.props['space'] == 'redshift':
                pos_arr = rspos
            computeHI(g, pos_arr, mass, density)

        return
    
    def temperatureMap(self, HIdensity):
        # assumes that the HIdensity is given in units (sm/(Mpc/h)^3)

        # convert to kg/m^3
        kgpsm = 1.989e30
        mpMpc = 3.086e22
        HIdensity = HIdensity*kgpsm/((mpMpc/self.header['HubbleParam'])**3)
        HIfq = 1420.4057e6 # Hz
        lam_12 = 2.9e-15 # inverse seconds
        factor = 3/32/sc.pi/sc.k/sc.m_p*sc.hbar*sc.c**3/HIfq**2*lam_12

        # Wolz says they use comoving volume - not sure if that'll affect the maps
        red_term = (1 + self.header['Redshift'])**2 / (self.header['HubbleParam'] * 100)
        return HIdensity * factor * red_term


    def _loadSnapshotData(self):
        f = hp.File(self.loadpath, 'r')
        pos = f['PartType0']['Coordinates'][:]
        vel = f['PartType0']['Velocities'][:]
        mass = f['PartType0']['Masses'][:]
        density = f['PartType0']['Density'][:]
        mass = self._convertMass(mass)
        pos = self._convertPos(pos)
        vel = self._convertVel(vel)
        density = self._convertDensity(density)
        f.close()
        return pos, vel, mass, density


class hiptl_nH(hiptl):

    def __init__(self, simname, snapshot, axis, resolution, chunk, pkl_path, verbose, 
            snappath, hih2filepath):
        super().__init__(simname, snapshot, axis, resolution, chunk, pkl_path, verbose, 
                snappath, hih2filepath, fieldname='hiptl_nH')

        self.vel_bins = np.logspace(-2, 6, 9)
        self.m_bins = np.logspace(-2, 8, 11)
        return
    
    def getGridProps(self):
        models = self.getMolFracModelsPtl()
        models.append('all_neut')
        nhbins = self._getnHBins()
        grp = {}
        for m in models:
            for idx in range(len(nhbins)):
                if idx == 0:
                    lo = 0
                    hi = nhbins[idx]
                elif idx == len(nhbins) - 1:
                    lo = nhbins[idx]
                    hi = np.inf
                else:
                    lo = nhbins[idx-1]
                    hi = nhbins[idx]

                n = [lo,hi]
                gp = hiptl_grid_props(m, 'CICW', self.fieldname,
                        nH = n)
                if gp.isIncluded():
                    grp[gp.getName()] = gp
        return grp

    def computeGrids(self, outfile):


        ################## FROM FIELD_SUPER BECAUSE PYTHON IS DUMB ################################
        if self.v:
            print("starting to compute grids...")
        if self.header is None:
            raise ValueError("header needs to be loaded before computing grids")
        dat = outfile.create_dataset('pickle', data=[0])
        dat.attrs['path'] = self.pkl_path
        if self.v:
            print("the saved pickle path: %s"%self.pkl_path)
        #########################################################################################
        
        
        hih2file = hp.File(self.hih2filepath, 'r')
        pos, vel, mass, density = self._loadSnapshotData()
        in_rss = False
        self.saved_hists = [] # vel-mass histograms saved to the outfile


        ############ HELPER FUNCTION ############################################
        def computeHI(gprop, pos, mass, density, is_in_rss):
            grid = Chunk(gprop.getName(), self.grid_resolution, self.chunk, verbose=self.v)
            if is_in_rss:
                grid.toRSS()

            if self.v:
                grid.print()

            bounds_nh = gprop.nH_bin
            kpctocm = 3.086e21
            smtog = 1.989e33
            m_p = 1.673e-24
            factor = 1/kpctocm**3 * smtog/m_p

            # get molecular fraction. we also want a bin that is all the neutral hydrogen,
            # this handles that case
            if not "all_neut" in gprop.model:
                molfrac = hih2file['PartType0']['f_mol_'+gprop.model][:]
            else:
                molfrac = np.zeros_like(mass)
            
            # getting data from hih2 files
            neutfrac = hih2file['PartType0']['f_neutral_H'][:]

            # getting the number density of hydrogen
            nH = density * neutfrac * factor

            # getting the mask
            mask = (nH >= bounds_nh[0]) & (nH < bounds_nh[1])

            
            # converting the masses to HI mass
            HImass = mass*(1-molfrac)*neutfrac

            # neutral fraction is -1 where models are not defined, 
            # so replace those values with 0
            HImass = np.where(HImass>=0, HImass, 
                    np.zeros(HImass.shape, dtype=np.float32))

            # place particles into grid
            grid.CICW(pos[mask, :], self.header['BoxSize'], HImass[mask])

            # save them to file
            self.saveData(outfile, grid, gprop)
            # if we are in redshift space, the grid handles saving with 'rs'

            # want to plot velocity vs mass for each nH bin
            # only need to do it for the first model, otherwise will just be a repeat.
            if gprop.props['nH_bin'] not in self.saved_hists:
                self.vel_mass_hist(vel[mask, :], mass[mask], gprop.props['nH_bin'], outfile)
                self.saved_hists.append(gprop.props['nH_bin'])

            return
        #############################################################################


        for g in self.gridprops.values():
            computeHI(g, pos, mass, density, in_rss)
        
        pos = self._toRedshiftSpace(pos, vel)
        in_rss = True

        for g in self.gridprops.values():
            computeHI(g, pos, mass, density, in_rss)
        hih2file.close()

        return

    def vel_mass_hist(self, vel, mass, dsetname, outfile):
        los_vel = vel[:, self.axis]
        
        hist = np.histogram2d(mass, los_vel, bins=[self.m_bins, self.vel_bins])[0]
        self.saveHist(outfile, hist, dsetname)
        return


    def saveHist(self, outfile, hist, dsetname):
        dat = outfile.create_dataset(dsetname, data=hist)
        dat.attrs['combine'] = -1
        dat.attrs['operation'] = 'hist'
        dat.attrs['gridname'] = -1 # indicates this is not for xpk computation
        return

    @staticmethod
    def _getnHBins():
        dendec = np.logspace(-4, 2, num=4)
        return dendec

    def getnHBinStrings(self):
        nH_bins = self._getnHBins()
        edges = np.zeros(len(nH_bins)+2)
        edges[1:-1] = nH_bins[:]
        edges[0] = 0
        edges[-1] = np.inf
        nH_str = {}
        for i in range(len(edges)-1):
            b = [edges[i], edges[i+1]]
            nH_str[i] = b
        return nH_str


class h2ptl(hiptl):

    def __init__(self, simname, snapshot, axis, resolution, chunk, pkl_path, 
                verbose, snappath, hih2filepath):
        super().__init__(simname, snapshot, axis, resolution, chunk, pkl_path, 
                verbose, snappath, hih2filepath, 'h2ptl')
        return
    
    def getGridProps(self):
        models = self.getMolFracModelsPtl()
        grp = {}
        for m in models:
            gp = hiptl_grid_props(m, 'CICW', self.fieldname)
            if gp.isIncluded():
                grp[gp.getName()] = gp
        return grp
    
    def computeGrids(self, outfile):
        ############### FROM FIELD_SUPER #################################################
        if self.v:
            print("starting to compute grids...")
        if self.header is None:
            raise ValueError("header needs to be loaded before computing grids")
        dat = outfile.create_dataset('pickle', data=[0])
        dat.attrs['path'] = self.pkl_path
        if self.v:
            print("the saved pickle path: %s"%self.pkl_path)
        ####################################################################################
        hih2file = hp.File(self.hih2filepath, 'r')
        pos, vel, mass, density = self._loadSnapshotData()

        temp = copy.copy(pos)
        rspos = self._toRedshiftSpace(temp, vel)
        del temp, vel, density


        ############ HELPER FUNCTION ############################################
        def computeH2(gprop, pos, mass):
            grid = Chunk(gprop.getName(), self.grid_resolution, self.chunk, verbose=self.v)
            
            if self.v:
                hs = '#' * 20
                print(hs+" COMPUTE H2 FOR %s "%(gprop.getName().upper()) + hs)

            # getting data from hih2 files
            neutfrac = hih2file['PartType0']['f_neutral_H'][:]
            neutfrac = neutfrac.astype('float32')
            neutfrac = np.where(neutfrac>=0, neutfrac, np.zeros_like(neutfrac))

            molfrac = hih2file['PartType0']['f_mol_'+gprop.model][:]
            molfrac = molfrac.astype('float32')
            molfrac = np.where(molfrac>=0, molfrac, np.zeros_like(molfrac))
            # converting the masses to H2 mass
            H2mass = mass*(molfrac)*neutfrac

            # place particles into grid
            grid.CICW(pos, self.header['BoxSize'], H2mass)

            # save them to file
            self.saveData(outfile, grid, gprop)
            # if we are in redshift space, the grid handles saving with 'rs'
            return
        #############################################################################

        for g in self.gridprops.values():
            if g.props['space'] == 'real':
                pos_arr = pos
            elif g.props['space'] == 'redshift':
                pos_arr = rspos
            computeH2(g, pos_arr, mass)
        
        hih2file.close()
        return
