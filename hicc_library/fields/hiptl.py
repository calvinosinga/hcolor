"""

"""
import h5py as hp
import numpy as np
from hicc_library.fields.field_super import Field
from hicc_library.grid.grid import Chunk

class hiptl(Field):

    def __init__(self, gd, simname, snapshot, axis, resolution, chunk, outfile):
        super().__init__(gd, simname, snapshot, axis, resolution, outfile)
        self.chunk = chunk
        self.gridnames = self.getMolFracModelsPtl()

        self.hih2file = hp.File(gd['hih2ptl']%chunk, 'r')
        
        self.loadsnap = gd['snapshot']%(chunk)
        self._loadSnapshotData()

        self.fieldname = 'hiptl'
        if gd['verbose']:
            print("finished constructor for %s, chunknum = %d"%(self.fieldname,chunk))
        return
    
    @staticmethod
    def getMolFracModelsPtl():
        return ['GD14', 'GK11', 'S14', 'K13']
    
    def computeGrids(self):
        for g in self.gridnames:
            self._computeHI(g)
        
        self._toRedshiftSpace()
        for g in self.gridnames:
            self._computeHI(g) # add the redshift moniker later, else get keyerror
        self.outfile.close()
        self.hih2file.close()
        return
    
    
    def _computeHI(self, gridname):
        
        self.grid = Chunk(gridname, self.resolution, self.chunk)
        self.grid.in_rss = self.in_rss
        
        if self.v:
            self.grid.print()

        # getting data from hih2 files
        neutfrac = self.hih2file['PartType0']['f_neutral_H'][:]
        molfrac = self.hih2file['PartType0']['f_mol_'+gridname][:]
        
        # converting the masses to HI mass
        self.mass *= (1-molfrac)*neutfrac

        # neutral fraction is -1 where models are not defined, 
        # so replace those values with 0
        self.mass = np.where(self.mass>=0, self.mass, 
                np.zeros(self.mass.shape, dtype=np.float32))

        # place particles into grid
        self.grid.CICW(self.pos, self.header['BoxSize'], self.mass)

        # save them to file
        self.saveData() # if we are in redshift space, the grid handles saving with 'rs'
        return

    
    def _loadSnapshotData(self):
        f = hp.File(self.loadsnap, 'r')
        self.pos = f['PartType0']['Coordinates'][:]
        self.vel = f['PartType0']['Velocities'][:]
        self.mass = f['PartType0']['Masses'][:]
        self._convertMass()
        self._convertPos()
        self._convertVel()
        f.close()
        return
    
