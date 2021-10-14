"""

"""
import h5py as hp
import numpy as np
from hicc_library.fields.field_super import Field, grid_props
from hicc_library.grid.grid import Chunk
import scipy.constants as sc

class hiptl_grid_props(grid_props):

    def __init__(self, base, mas, field, mass_or_temp = None, nH = None):
        other = {}
        other['mass'] = mass_or_temp
        if not nH is None:
            self.nH_bin = nH
            nH_str = str(nH)
            other['nH_bin'] = nH_str
        else:
            other['nH_bin'] = nH
        self.model = base
        super().__init__(base, mas, field, other)
        return
    
    def isCompatible(self, other):
        sp = self.props
        op = other.props
        if sp['mass'] == 'temp':
            if 'galaxy' in op['field']:
                res = ['eBOSS', 'wiggleZ', '2df']
                return op['resdef'] in res
            else:
                return False
        else:
            return True

    
class hiptl(Field):

    def __init__(self, simname, snapshot, axis, resolution, chunk, pkl_path, 
                verbose, snappath, hih2filepath, fieldname = 'hiptl'):
        super().__init__(simname, snapshot, axis, resolution, pkl_path, verbose)
        self.chunk = chunk

        self.fieldname = fieldname
        self.hih2filepath = hih2filepath%self.chunk
        self.loadpath = snappath%self.chunk
        return
    
    def getGridProps(self):
        models = self.getMolFracModelsPtl()
        mass_or_temp = ['mass', 'temp']
        grp = {}
        for m in models:
            for mt in mass_or_temp:
                gp = hiptl_grid_props(m, 'CICW', self.fieldname, mass_or_temp = mt)
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
        in_rss = False


        ############ HELPER FUNCTION ############################################
        def computeHI(gprop, pos, mass, density, is_in_rss):
            grid = Chunk(gprop.getName(), self.resolution, self.chunk, verbose=self.v)
            if is_in_rss:
                grid.toRSS()
            
            if self.v:
                hs = '#' * 20
                print(hs+" COMPUTE HI FOR %s "%(gprop.getName().upper()) + hs)
                print("is in redshift space?:%s"%str(is_in_rss))
                print("does the grid agree?:%s"%str(is_in_rss))

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
            if gprop.props["mass"] == 'temp':
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
            computeHI(g, pos, mass, density, in_rss)
        
        pos = self._toRedshiftSpace(pos, vel)
        in_rss = True
        
        for g in list(self.gridprops.values()):
            computeHI(g, pos, mass, density, in_rss)
        hih2file.close()
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
        saved_hists = [] # vel-mass histograms saved to the outfile


        ############ HELPER FUNCTION ############################################
        def computeHI(gprop, pos, mass, density, is_in_rss):
            grid = Chunk(gprop.getName(), self.resolution, self.chunk, verbose=self.v)
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
            if gprop.props['nH_bin'] not in saved_hists:
                self.vel_mass_hist(vel[mask, :], mass[mask], gprop.props['nH_bin'], outfile)
                saved_hists.append(gprop.props['nH_bin'])

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
        in_rss = False


        ############ HELPER FUNCTION ############################################
        def computeH2(gprop, pos, mass, is_in_rss):
            grid = Chunk(gprop.getName(), self.resolution, self.chunk, verbose=self.v)
            if is_in_rss:
                grid.toRSS()
            
            if self.v:
                hs = '#' * 20
                print(hs+" COMPUTE H2 FOR %s "%(gprop.getName().upper()) + hs)
                print("is in redshift space?:%s"%str(is_in_rss))
                print("does the grid agree?:%s"%str(is_in_rss))

            # getting data from hih2 files
            neutfrac = hih2file['PartType0']['f_neutral_H'][:]
            molfrac = hih2file['PartType0']['f_mol_'+gprop.model][:]
            
            # converting the masses to HI mass
            H2mass = mass*(molfrac)*neutfrac

            # neutral fraction is -1 where models are not defined, 
            # so replace those values with 0
            H2mass = np.where(H2mass>=0, H2mass, 
                    np.zeros(H2mass.shape, dtype=np.float32))

            # place particles into grid
            grid.CICW(pos, self.header['BoxSize'], H2mass)

            # save them to file
            self.saveData(outfile, grid, gprop)
            # if we are in redshift space, the grid handles saving with 'rs'
            return
        #############################################################################

        for g in self.gridprops.values():
            computeH2(g, pos, mass, in_rss)
        
        pos = self._toRedshiftSpace(pos, vel)
        in_rss = True
        
        for g in self.gridprops.values():
            computeH2(g, pos, mass, in_rss)
        hih2file.close()
        return
