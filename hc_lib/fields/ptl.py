"""

"""
import h5py as hp
import numpy as np
import copy
from hc_lib.fields.field_super import Field
from hc_lib.grid.grid import Chunk
from hc_lib.grid.grid_props import ptl_grid_props


    
class ptl(Field):

    def __init__(self, simname, snapshot, axis, resolution, chunk, pkl_path, 
            verbose, snappath):
        
        self.fieldname = 'ptl'
        self.chunk = chunk
        
        self.loadpath = snappath%(chunk)
                
        super().__init__(simname, snapshot, axis, resolution, pkl_path, verbose)
        if self.v:
            print("finished constructor for %s, chunknum = %d"%(self.fieldname,chunk))
        return
    
    def getGridProps(self):
        grp = {}
        grids = ['ptl', 'dm', 'stmass']
        spaces = ['real', 'redshift']
        for g in grids:
            for s in spaces:
                gp = ptl_grid_props("CICW", self.fieldname, s, g)
                if gp.isIncluded():
                    grp[gp.getH5DsetName()] = gp
        return grp

    def computeGrids(self, outfile):
        pos, vel, mass, slices = self._loadSnapshotData()
        super().setupGrids(outfile)

        temp = copy.copy(pos)
        rspos = self._toRedshiftSpace(temp, vel)
        del temp, vel

        ############# HELPER METHOD ##################################
        def computePtl(gprop, pos, mass, slc):
        
            grid = Chunk(gprop.getH5DsetName(), self.grid_resolution, self.chunk, verbose=self.v)
            
            if self.v:
                grid.print()
            
            # place particles into grid
            grid.CICW(pos[slc, :], self.header['BoxSize'], mass[slc])

            # save them to file
            self.saveData(outfile, grid, gprop)
            return
        ################################################################

        for g in list(self.gridprops.values()):
            if g.props['species'] == 'stmass':
                slc = slices[2]
            elif g.props['species'] == 'dm':
                slc = slices[1]
            else:
                slc = slice(None)
            
            if g.props['space'] == 'real':
                pos_arr = pos
            elif g.props['space'] == 'redshift':
                pos_arr = rspos
            computePtl(g, pos_arr, mass, slc)
        
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

