"""

"""
import h5py as hp
import numpy as np
from hc_lib.fields.field_super import Field, grid_props
from hc_lib.grid.grid import Chunk
from HI_library import HI_mass_from_Illustris_snap as vnhi
import scipy.constants as sc


class vn_grid_props(grid_props):
    def __init__(self, base, mas, field, mass_or_temp):
        other = {}
        other['mass'] = mass_or_temp

        super().__init__(base, mas, field, other)
    
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
        gnames = ['vn']
        MorT = ['mass', 'temp']
        grp = {}
        for g in gnames:
            for mt in MorT:
                gp = vn_grid_props(g, "CICW", self.fieldname, mt)
                if gp.isIncluded():
                    grp[gp.getName()] = gp

        return grp
    
    def computeGrids(self, outfile):
        pos, vel, mass, volume = self._loadSnapshotData()
        in_rss = False
        super().computeGrids(outfile)
        ############# HELPER METHOD ##################################
        def computeHI(gprop, pos, mass, volume, is_in_rss):
        
            grid = Chunk(gprop.getName(), self.resolution, self.chunk, verbose = self.v)
            if is_in_rss:
                grid.toRSS()
            
            if self.v:
                grid.print()
            # place particles into grid
            if gprop.props['mass'] == 'temp':
                T_HI = self.temperatureMap(mass / volume)
                grid.CICW(pos, self.header['BoxSize'], T_HI)
            
            else:
                grid.CICW(pos, self.header['BoxSize'], mass)

            # save them to file
            self.saveData(outfile, grid, gprop)
            return

        for g in list(self.gridprops.values()):
            computeHI(g, pos, mass, volume, in_rss)
        
        pos = self._toRedshiftSpace(pos, vel)
        in_rss = True
        for g in list(self.gridprops.values()):
            computeHI(g, pos, mass, volume, in_rss)
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
