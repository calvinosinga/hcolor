"""

"""
import h5py as hp
import numpy as np
from numpy.core.defchararray import count
from hicc_library.fields.field_super import Field
from hicc_library.grid.grid import Chunk

class hiptl(Field):

    def __init__(self, simname, snapshot, axis, resolution, chunk, pkl_path, 
                verbose, snappath, hih2filepath):
        super().__init__(simname, snapshot, axis, resolution, pkl_path, verbose)
        self.chunk = chunk
        self.gridnames = self.getMolFracModelsPtl()

        self.fieldname = 'hiptl'
        self.hih2filepath = hih2filepath%self.chunk
        self.loadpath = snappath%self.chunk

        if self.v:
            print("finished constructor for %s, chunknum = %d"%(self.fieldname,chunk))
        return
    
    @staticmethod
    def getMolFracModelsPtl():
        return ['GD14', 'GK11', 'S14', 'K13']
    
    def computeGrids(self, outfile):
        super().computeGrids(outfile)
        hih2file = hp.File(self.hih2filepath, 'r')
        pos, vel, mass = self._loadSnapshotData()
        in_rss = False


        ############ HELPER FUNCTION ############################################
        def computeHI(gridname, mass):
            grid = Chunk(gridname, self.resolution, self.chunk, verbose=self.v)
            grid.in_rss = in_rss
            
            if self.v:
                grid.print()

            # getting data from hih2 files
            neutfrac = hih2file['PartType0']['f_neutral_H'][:]
            molfrac = hih2file['PartType0']['f_mol_'+gridname][:]
            
            # converting the masses to HI mass
            mass *= (1-molfrac)*neutfrac

            # neutral fraction is -1 where models are not defined, 
            # so replace those values with 0
            mass = np.where(mass>=0, mass, 
                    np.zeros(mass.shape, dtype=np.float32))

            # place particles into grid
            grid.CICW(pos, self.header['BoxSize'], mass)

            # save them to file
            self.saveData(outfile, grid)
            # if we are in redshift space, the grid handles saving with 'rs'
            return
        #############################################################################

        for g in self.gridnames:
            computeHI(g, mass)
        
        pos = self._toRedshiftSpace(pos, vel)
        in_rss = True
        
        for g in self.gridnames:
            computeHI(g, mass)
        hih2file.close()
        return
    
    
    def _loadSnapshotData(self):
        f = hp.File(self.loadpath, 'r')
        pos = f['PartType0']['Coordinates'][:]
        vel = f['PartType0']['Velocities'][:]
        mass = f['PartType0']['Masses'][:]
        mass = self._convertMass(mass)
        pos = self._convertPos(pos)
        vel = self._convertVel(vel)
        f.close()
        return pos, vel, mass






class hiptl_nH(hiptl):

    def __init__(self, simname, snapshot, axis, resolution, chunk, pkl_path, verbose, 
            snappath, hih2filepath):
        super().__init__(simname, snapshot, axis, resolution, chunk, pkl_path, verbose, 
                snappath, hih2filepath)
        self.fieldname = 'hiptl_nH'
        
        mods = self.getMolFracModelsPtl()
        mods.append('all_neut')
        nh_bins = self._getnHBins()
        self.gridnames = []
        self.vel_mass_xbins = None
        self.vel_mass_ybins = None
        for m in mods:
            for n in range(len(nh_bins)+1):
                self.gridnames.append(m+str(n))
        
        return
    
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
        nHbins = self._getnHBins()
        saved_hists = [] # vel-mass histograms saved to the outfile
        ############ HELPER FUNCTION ############################################
        def computeHI(gridname, mass):
            grid = Chunk(gridname, self.resolution, self.chunk, verbose=self.v)
            grid.in_rss = in_rss

            if self.v:
                grid.print()
            
            # get the lower and upper bounds for the nH bin.
            # handles edge cases as well
            idx = int(gridname[-1])
            if idx == 0:
                lo = 0
                hi = nHbins[idx]
            elif idx == len(nHbins):
                lo = nHbins[-1]
                hi = np.inf
            else:
                lo=nHbins[idx-1]
                hi=nHbins[idx]
            
            kpctocm = 3.086e21
            smtog = 1.989e33
            m_p = 1.673e-24
            factor = 1/kpctocm**3 * smtog/m_p

            # get molecular fraction. we also want a bin that is all the neutral hydrogen,
            # this handles that case
            if not "all_neut" in gridname:
                molfrac = hih2file['PartType0']['f_mol_'+gridname[:-1]][:]
            else:
                molfrac = np.zeros_like(mass)
            
            # getting data from hih2 files
            neutfrac = hih2file['PartType0']['f_neutral_H'][:]

            # getting the number density of hydrogen
            nH = density * neutfrac * factor

            # getting the mask
            mask = (nH >= lo) & (nH < hi)

            
            # converting the masses to HI mass
            mass *= (1-molfrac)*neutfrac

            # neutral fraction is -1 where models are not defined, 
            # so replace those values with 0
            mass = np.where(mass>=0, mass, 
                    np.zeros(mass.shape, dtype=np.float32))

            # place particles into grid
            grid.CICW(pos[mask, :], self.header['BoxSize'], mass[mask])

            # save them to file
            self.saveData(outfile, grid, lo, hi)
            # if we are in redshift space, the grid handles saving with 'rs'

            # want to plot velocity vs mass for each nH bin
            # only need to do it for the first model, otherwise will just be a repeat.
            dsetname = str([lo, hi])
            if dsetname not in saved_hists:
                self.vel_mass_hist(vel[mask, :], mass[mask], dsetname, outfile)
                saved_hists.append(dsetname)

            return
        #############################################################################


        for g in self.gridnames:
            computeHI(g, mass)
        
        pos = self._toRedshiftSpace(pos, vel)
        in_rss = True

        for g in self.gridnames:
            computeHI(g, mass)
        hih2file.close()

        return

    def vel_mass_hist(self, vel, mass, dsetname, outfile):
        vel_bins = np.logspace(-2, 6, 9)
        m_bins = np.logspace(-2, 8, 11)
        speed = np.sum(vel**2, axis=1)
        speed = speed**0.5
        outfile.create_dataset(dsetname, data = np.histogram2d(mass, speed, bins=[m_bins, vel_bins])[0])
        self.vel_bins = vel_bins
        self.m_bins = m_bins
        return

    def saveData(self, outfile, grid, lo, hi):
        dat = super().saveData(outfile, grid)
        dat.attrs["nH_range"] = (lo, hi)
        return

    @staticmethod
    def _getnHBins():
        dendec = np.logspace(-4, 2, num=4)
        return dendec
    
    def _loadSnapshotData(self):
        pos, vel, mass = super()._loadSnapshotData()
        f = hp.File(self.loadpath, 'r')
        density = f['PartType0']['Density'][:]
        density = self._convertDensity(density)
        f.close()
        return pos, vel, mass, density
    
    def _convertDensity(self, rho):
        """
        converts density from 1e10 solar mass/h / (ckpc/h)**3 to sm/kpc^3
        """

        h = self.header['HubbleParam']
        rho *= 1e10/h/ self.header['Time']**3 * h**3
        # converts rho to sm/kpc^3
        return rho


