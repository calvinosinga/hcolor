"""

"""
import h5py as hp
import numpy as np
from hicc_library.fields.field_super import Field
from hicc_library.grid.grid import Chunk


class ptl(Field):

    def __init__(self, simname, snapshot, axis, resolution, chunk, pkl_path, 
            verbose, snappath):
        super().__init__(simname, snapshot, axis, resolution, pkl_path, verbose)
        self.fieldname = 'ptl'
        self.chunk = chunk
        self.gridnames = ['ptl']
        
        self.loadpath = snappath%(chunk)
        
        if self.v:
            print("finished constructor for %s, chunknum = %d"%(self.fieldname,chunk))
        return
    

    def computeGrids(self, outfile):
        pos, vel, mass = self._loadSnapshotData()
        in_rss = False
        super().computeGrids(outfile)
        ############# HELPER METHOD ##################################
        def computePtl(gridname):
        
            grid = Chunk(gridname, self.resolution, self.chunk, verbose=self.v)
            grid.in_rss = in_rss
            
            if self.v:
                grid.print()
            
            # place particles into grid
            grid.CICW(pos, self.header['BoxSize'], mass)

            # save them to file
            self.saveData(outfile, grid)
            return
        
        for g in self.gridnames:
            computePtl(g)
        
        pos = self._toRedshiftSpace(pos, vel)
        in_rss = True
        for g in self.gridnames:
            computePtl(g)
        return
    
    
    def _loadSnapshotData(self):
        snap = hp.File(self.loadpath, 'r')
        atts = dict(snap['Header'].attrs)
        nptl = atts['NumPart_ThisFile']
        dmmass = atts['MassTable'][1]
        ptltypes = [0,1,4,5]
        totptl = 0
        for p in ptltypes:
            totptl += nptl[p]
        pos = np.zeros((totptl, 3), dtype=np.float32)
        vel = np.zeros((totptl, 3), dtype=np.float32)
        mass = np.zeros((totptl), dtype=np.float32)
        idx = 0
        for p in ptltypes:
            pos[idx:idx+nptl[p]] = snap['PartType%d'%p]['Coordinates'][:]
            vel[idx:idx+nptl[p]] = snap['PartType%d'%p]['Velocities'][:]
            if p == 1:
                mass[idx:idx+nptl[p]] = dmmass
            else:
                mass[idx:idx+nptl[p]] = snap['PartType%d'%p]['Masses'][:]
        pos = self._convertPos(pos)
        mass = self._convertMass(mass)
        vel = self._convertVel(vel)
        return pos, vel, mass

