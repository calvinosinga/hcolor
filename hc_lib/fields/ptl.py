"""

"""
import h5py as hp
import numpy as np
from hc_lib.fields.field_super import Field, grid_props
from hc_lib.grid.grid import Chunk

class ptl_grid_props(grid_props):
    
    def __init__(self, base, mas, field):
        self.type = base
        super().__init__(base, mas, field, {})
        return
    
class ptl(Field):

    def __init__(self, simname, snapshot, axis, resolution, chunk, pkl_path, 
            verbose, snappath):
        
        self.fieldname = 'ptl'
        self.chunk = chunk
        
        self.loadpath = snappath%(chunk)
        
        self.isHI = False
        
        super().__init__(simname, snapshot, axis, resolution, pkl_path, verbose)
        if self.v:
            print("finished constructor for %s, chunknum = %d"%(self.fieldname,chunk))
        return
    
    def getGridProps(self):
        grp = {}
        grids = ['ptl', 'dm', 'stmass']
        for g in grids:
            gp = ptl_grid_props(g, "CICW", self.fieldname)
            if gp.isIncluded():
                grp[gp.getName()] = gp
        return grp

    def computeGrids(self, outfile):
        pos, vel, mass, slices = self._loadSnapshotData()
        in_rss = False
        super().computeGrids(outfile)
        ############# HELPER METHOD ##################################
        def computePtl(gprop, pos, mass, slc, is_in_rss):
        
            grid = Chunk(gprop.getName(), self.resolution, self.chunk, verbose=self.v)
            if is_in_rss:
                grid.toRSS()
            
            if self.v:
                grid.print()
            
            # place particles into grid
            grid.CICW(pos[slc, :], self.header['BoxSize'], mass[slc])

            # save them to file
            self.saveData(outfile, grid, gprop)
            return
        
        for g in list(self.gridprops.values()):
            if g.type == 'stmass':
                slc = slices[2]
            elif g.type == 'dm':
                slc = slices[1]
            else:
                slc = slice(None)
            computePtl(g, pos, mass, slc, in_rss)
        
        pos = self._toRedshiftSpace(pos, vel)
        in_rss = True
        for g in list(self.gridprops.values()):
            if g.type == 'stmass':
                slc = slices[2]
            elif g.type == 'dm':
                slc = slices[1]
            else:
                slc = slice(None)

            computePtl(g, pos, mass, slc, in_rss)
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
        slices = []
        for p in ptltypes:
            slices.append(slice(idx, idx + nptl[p]))
            pos[idx:idx+nptl[p]] = snap['PartType%d'%p]['Coordinates'][:]
            vel[idx:idx+nptl[p]] = snap['PartType%d'%p]['Velocities'][:]
            if p == 1:
                mass[idx:idx+nptl[p]] = dmmass
            else:
                mass[idx:idx+nptl[p]] = snap['PartType%d'%p]['Masses'][:]
        pos = self._convertPos(pos)
        mass = self._convertMass(mass)
        vel = self._convertVel(vel)
        return pos, vel, mass, slices

