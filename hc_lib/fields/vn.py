"""

"""
import h5py as hp
import numpy as np
from hc_lib.fields.field_super import Field
from hc_lib.grid.grid import Chunk
import copy
from HI_library import HI_mass_from_Illustris_snap as vnhi
import scipy.constants as sc
from hc_lib.grid.grid_props import vn_grid_props

class vn(Field):

    def __init__(self, simname, snapshot, axis, resolution, chunk, pkl_path, 
            verbose, snappath, treecoolpath):
        
        self.fieldname = 'vn'
        self.chunk = chunk
        self.TREECOOL = treecoolpath
        
        self.loadpath = snappath%(chunk)
        super().__init__(simname, snapshot, axis, resolution, pkl_path, verbose)
        if self.v:
            print("finished constructor for %s, chunknum = %d"%(self.fieldname,chunk))
        return
    
    def getGridProps(self):
        MorT = ['mass', 'temp']
        spaces = ['real', 'redshift']
        grp = {}
        for s in spaces:
            for mt in MorT:
                gp = vn_grid_props("CICW", self.fieldname, s, mt)
                if gp.isIncluded():
                    grp[gp.getH5DsetName()] = gp

        return grp
    
    def computeGrids(self, outfile):
        super().setupGrids(outfile)

        pos, vel, mass, volume = self._loadSnapshotData()
        temp = copy.copy(pos)
        rspos = self._toRedshiftSpace(temp, vel)
        del temp, vel
        
        ############# HELPER METHOD ##################################
        def computeHI(gprop, pos, mass, volume):
        
            grid = Chunk(gprop.getH5DsetName(), self.grid_resolution, self.chunk, verbose = self.v)

            
            if self.v:
                grid.print()
            # place particles into grid
            if gprop.props['map'] == 'temp':
                T_HI = self.temperatureMap(mass / volume)
                grid.CICW(pos, self.header['BoxSize'], T_HI)
            
            else:
                grid.CICW(pos, self.header['BoxSize'], mass)

            # save them to file
            self.saveData(outfile, grid, gprop)
            return

        for g in list(self.gridprops.values()):
            if g.props['space'] == 'real':
                pos_arr = pos
            elif g.props['space'] == 'redshift':
                pos_arr = rspos
            computeHI(g, pos_arr, mass, volume)
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
        pos, mass = vnhi(self.loadpath, self.TREECOOL)
        pos = self._convertPos(pos)
        mass = self._convertMass(mass)
        snap = hp.File(self.loadpath, 'r')
        vel = snap['PartType0']['Velocities'][:]
        density = snap['PartType0']['Density'][:]
        gas_mass = snap['PartType0']['Masses'][:]

        volume = density / gas_mass
        volume *= (self.header["Time"]/1e3)**3
        snap.close()
        vel = self._convertVel(vel)
        return pos, vel, mass, volume
    # these have to be redefined since Paco uses solar/h for mass and
    # cMpc/h for position
    def _convertPos(self, pos=None):
        pos *= self.header['Time']
        return pos
    
    def _convertMass(self, mass=None):
        mass *= 1/self.header['HubbleParam']
        return mass
