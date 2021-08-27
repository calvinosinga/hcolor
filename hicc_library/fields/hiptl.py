"""

"""
import h5py as hp
import numpy as np
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
        def computeHI(gridname):
            grid = Chunk(gridname, self.resolution, self.chunk)
            grid.in_rss = in_rss
            
            if self.v:
                self.grid.print()

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
            self.grid.CICW(pos, self.header['BoxSize'], mass)

            # save them to file
            self.saveData(outfile, grid)
            # if we are in redshift space, the grid handles saving with 'rs'
            return
        #############################################################################

        for g in self.gridnames:
            computeHI(g)
        
        pos = self._toRedshiftSpace(pos, vel)
        in_rss = True
        
        for g in self.gridnames:
            computeHI(g)
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
    
