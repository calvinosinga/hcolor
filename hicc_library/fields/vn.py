"""

"""
import h5py as hp
import numpy as np
from hicc_library.fields.field_super import Field
from hicc_library.grid.grid import Chunk
from HI_library import HI_mass_from_Illustris_snap as vnhi

class vn(Field):

    def __init__(self, simname, snapshot, axis, resolution, chunk, pkl_path, 
            verbose, snappath, treecoolpath):
        super().__init__(simname, snapshot, axis, resolution, pkl_path, verbose)
        self.fieldname = 'vn'
        self.chunk = chunk
        self.gridnames = ['vn']
        self.TREECOOL = treecoolpath
        
        self.loadpath = snappath%(chunk)
        
        if self.v:
            print("finished constructor for %s, chunknum = %d"%(self.fieldname,chunk))
        return
    

    def computeGrids(self, outfile):
        pos, vel, mass = self._loadSnapshotData()
        in_rss = False
        super().computeGrids(outfile)
        ############# HELPER METHOD ##################################
        def computeHI(gridname):
        
            grid = Chunk(gridname, self.resolution, self.chunk, verbose = self.v)
            grid.in_rss = in_rss
            
            if self.v:
                grid.print()
            
            # place particles into grid
            grid.CICW(pos, self.header['BoxSize'], mass)

            # save them to file
            self.saveData(outfile, grid)
            return

        for g in self.gridnames:
            computeHI(g)
        
        pos = self._toRedshiftSpace(pos, vel)
        in_rss = True
        for g in self.gridnames:
            computeHI(g)
        return
    
    
    def _loadSnapshotData(self):
        pos, mass = vnhi(self.loadpath, self.TREECOOL)
        pos = self._convertPos(pos)
        mass = self._convertMass(mass)
        snap = hp.File(self.loadpath, 'r')
        vel = snap['PartType0']['Velocities'][:]
        snap.close()
        vel = self._convertVel(vel)
        return pos, vel, mass
    # these have to be redefined since Paco uses solar/h for mass and
    # cMpc for position
    def _convertPos(self, pos=None):
 
        pos *= self.header['Time']
        return pos
    
    def _convertMass(self, mass=None):
        mass *= 1/self.header['HubbleParam']
        return mass
