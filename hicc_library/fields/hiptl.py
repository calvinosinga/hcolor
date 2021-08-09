"""

"""
import h5py as hp
import numpy as np
from hicc_library.fields.field_super import Field
from hicc_library.grid.grid import Chunk

class hiptl(Field):

    def __init__(self, paths, simname, snapshot, resolution, chunk):
        super().__init__(paths, simname, snapshot, resolution)

        self.chunk = chunk
        self.gridnames = ['GD14', 'GK11', 'S14', 'K13']
        self.priority = [1,1,1,1]
        self.priority = {self.gridnames[i]:self.priority[i] for i in range(len(self.priority))}
        self.gridsave = hp.File(paths['grids'] + 
                "hiptl%s_%03d.%d.hdf5"%(simname,snapshot,chunk), 'w')

        self.hih2file = hp.File(paths['hih2ptl'] +
                "hih2_particles_%03d.%d.hdf5"%(snapshot,chunk), 'r')
        
        self.loadsnap = paths['snapshot']+'snap_%03d.%d.hdf5'
        self._loadSnapshotData()
        return
    
    def computeGrids(self):
        for g in self.gridnames:
            self._computeHI(g)
        
        self.gridsave.close()
        return
    
    
    def _computeHI(self, gridname):
        
        self.grid = Chunk(gridname, self.resolution, self.chunk)
        
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
        self._saveHI(gridname)

        # now create new chunk for redshift space
        gridname = gridname+'rs'
        self.grid = Chunk(gridname, self.resolution, self.chunk)
        self._toRedshiftSpace()

        if self.grid.in_rss:
            self.grid.CICW(self.pos, self.header['BoxSize'], self.mass)
        else:
            raise ValueError("the grid does not know that we are in redshift-space!")
        
        self._saveHI(gridname)
        return
    
    def _saveHI(self, gridname):
        dat = self.gridsave.create_dataset(gridname, data=self.grid.getGrid(), 
                compression="gzip", compression_opts=9)
        dat.attrs["in_rss"] = self.grid.in_rss
        dat.attrs["num_constituent"] = self.grid.combine
        dat.attrs["chunks"] = self.grid.chunk_nums
        dat.attrs["priority"] = self.priority[gridname]
        return
    
    def _loadSnapshotData(self):
        f = hp.File(self.loadsnap, 'r')
        self.pos = f['PartType0']['Coordinates'][:]
        self.vel = f['PartType0']['Velocities'][:]
        self.mass = f['PartType0']['Masses'][:]
        self._convertMass()
        self._convertPos()
        self._convertVel()
        return
    
