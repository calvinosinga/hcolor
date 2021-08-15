"""

"""
import h5py as hp
import numpy as np
from hicc_library.fields.field_super import Field
from hicc_library.grid.grid import Chunk
from HI_library import HI_mass_from_Illustris_snap as vnhi

class vn(Field):

    def __init__(self, gd, simname, snapshot, axis, resolution, chunk, outfile):
        super().__init__(gd, simname, snapshot, axis, resolution, outfile)
        self.fieldname = 'vn'
        self.chunk = chunk
        self.gridnames = ['vn']
        self.TREECOOL = gd['TREECOOL']
        
        self.loadsnap = gd['snapshot']%(chunk)

        
        if gd['verbose']:
            print("finished constructor for %s, chunknum = %d"%(self.fieldname,chunk))
        self._loadSnapshotData()
        return
    

    def computeGrids(self):
        for g in self.gridnames:
            self._computeHI(g)
        
        self._toRedshiftSpace()
        for g in self.gridnames:
            self._computeHI(g+'rs')
        self.outfile.close()
        return
    
    
    def _computeHI(self, gridname):
        
        self.grid = Chunk(gridname, self.resolution, self.chunk)
        self.grid.in_rss = self.in_rss
        
        if self.v:
            self.grid.print()
        
        # place particles into grid
        self.grid.CICW(self.pos, self.header['BoxSize'], self.mass)

        # save them to file
        self.saveData()
        return
    
    def _loadSnapshotData(self):
        self.pos, self.mass = vnhi(self.loadsnap, self.TREECOOL)
        self._convertPos()
        self._convertMass()
        snap = hp.File(self.loadsnap, 'r')
        self.vel = snap['PartType0']['Velocities']
        snap.close()
        self._convertVel()
        return
    # these have to be redefined since Paco uses solar/h for mass and
    # cMpc for position
    def _convertPos(self, pos=None):
        if pos is None:
            self.pos *= self.header['Time']
            return
        else:
            pos *= self.header['Time']
            return pos
    
    def _convertMass(self, mass=None):
        if mass is None:
            self.mass *= 1/self.header['HubbleParam']
            return
        else:
            mass *= 1/self.header['HubbleParam']
            return mass
