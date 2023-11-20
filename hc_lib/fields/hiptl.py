"""

"""
import h5py as hp
import numpy as np
from hc_lib.fields.field_super import Field
from hc_lib.grid.grid import Chunk, VelChunk
import copy
import scipy.constants as sc
from hc_lib.grid.grid_props import hiptl_grid_props
from hc_lib.fields.run_lib import getMolFracModelsPtl

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
        models = getMolFracModelsPtl()
        # mass_or_temp = ['mass', 'temp']
        mass_or_temp = ['mass']
        spaces = ['redshift', 'real']
        types = ['vel', 'mass']
        grp = {}
        for s in spaces:
            for m in models:
                for tp in types:
                    for mt in mass_or_temp:
                        if not (tp == 'vel' and s == 'redshift'):
                            gp = hiptl_grid_props('CICW', self.fieldname, s, tp, m, mass_or_temp = mt)
                            if gp.isIncluded():
                                grp[gp.getH5DsetName()] = gp
        return grp
    
    
    def computeGrids(self, outfile):
        super().setupGrids(outfile)
        hih2file = hp.File(self.hih2filepath, 'r')
        pos, vel, mass, density = self._loadSnapshotData()
        temp = copy.copy(pos)
        rspos = self._toRedshiftSpace(temp, vel)
        del temp

        ############ HELPER FUNCTION ############################################
        def computeHI(gprop, pos, mass, density):
            gprop.props['type'] = 'mass'
            grid = Chunk(gprop.getH5DsetName(), self.grid_resolution, self.chunk, verbose=self.v)
            
            if self.v:
                hs = '#' * 20
                print(hs+" COMPUTE HI FOR %s "%(gprop.getH5DsetName().upper()) + hs)

            # getting data from hih2 files
            neutfrac = hih2file['PartType0']['f_neutral_H'][:]
            molfrac = hih2file['PartType0']['f_mol_'+gprop.props['model']][:]
            
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
            return
        
        def computeVel(gprop, pos, vel):
            gprop.props['type'] = 'vel'
            grid = VelChunk(gprop.getH5DsetName(), self.grid_resolution, self.chunk, verbose = self.v)

            if self.v:
                hs = '#' * 20
                print(hs+" COMPUTE HI VEL FOR %s "%(gprop.getH5DsetName().upper()) + hs)
            
            grid.CICW(pos, self.header['BoxSize'], vel)
            self.saveData(outfile, grid, gprop)
            return
        #############################################################################

        for g in list(self.gridprops.values()):
            if g.props['space'] == 'real':
                pos_arr = pos
                computeVel(g, pos_arr, vel)
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
        vel = self._convertVel(vel) # removes root a
        density = self._convertDensity(density)
        f.close()
        return pos, vel, mass, density


class h2ptl(hiptl):

    def __init__(self, simname, snapshot, axis, resolution, chunk, pkl_path, 
                verbose, snappath, hih2filepath):
        super().__init__(simname, snapshot, axis, resolution, chunk, pkl_path, 
                verbose, snappath, hih2filepath, 'h2ptl')
        return
    
    def getGridProps(self):
        models = getMolFracModelsPtl()
        grp = {}
        for m in models:
            gp = hiptl_grid_props(m, 'CICW', self.fieldname)
            if gp.isIncluded():
                grp[gp.getH5DsetName()] = gp
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
            grid = Chunk(gprop.getH5DsetName(), self.grid_resolution, self.chunk, verbose=self.v)
            
            if self.v:
                hs = '#' * 20
                print(hs+" COMPUTE H2 FOR %s "%(gprop.getH5DsetName().upper()) + hs)

            # getting data from hih2 files
            neutfrac = hih2file['PartType0']['f_neutral_H'][:]
            neutfrac = neutfrac.astype('float32')
            neutfrac = np.where(neutfrac>=0, neutfrac, np.zeros_like(neutfrac))

            molfrac = hih2file['PartType0']['f_mol_'+gprop.props['model']][:]
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
