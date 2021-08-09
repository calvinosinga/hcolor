"""
This file defines two grid classes 
"""

import numpy as np
import h5py as hp

class Grid():

    def __init__(self, res):
        self.grid = np.zeros((res,res,res), dtype=np.float32)
        self.in_rss = False
        self.is_computed = False
        return
    
    def getGrid(self):
        if not self.is_computed:
            raise RuntimeError("grid is empty; has not been computed")
        return self.grid
    
    def toRSS(self):
        self.in_rss = True
        return
    
    def isChunk(self):
        return False
    
    def getResolution(self):
        return self.grid.shape[0]
    
    def CICW(self, pos, boxsize, mass):
        ptls = pos.shape[0]; coord = pos.shape[1]; dims = self.grid.shape[0]
        inv_cell_size = dims/boxsize
        
        index_d = np.zeros(3, dtype=np.int64)
        index_u = np.zeros(3, dtype=np.int64)
        d = np.zeros(3)
        u = np.zeros(3)

        for i in range(ptls):
            for axis in range(coord):
                dist = pos[i,axis] * inv_cell_size
                u[axis] = dist - int(dist)
                d[axis] = 1 - u[axis]
                index_d[axis] = (int(dist))%dims
                index_u[axis] = index_d[axis] + 1
                index_u[axis] = index_u[axis]%dims #seems this is faster
            self.grid[index_d[0],index_d[1],index_u[2]] += d[0]*d[1]*u[2]*mass[i]
            self.grid[index_d[0],index_u[1],index_d[2]] += d[0]*u[1]*d[2]*mass[i]
            self.grid[index_d[0],index_u[1],index_u[2]] += d[0]*u[1]*u[2]*mass[i]
            self.grid[index_u[0],index_d[1],index_d[2]] += u[0]*d[1]*d[2]*mass[i]
            self.grid[index_u[0],index_d[1],index_u[2]] += u[0]*d[1]*u[2]*mass[i]
            self.grid[index_u[0],index_u[1],index_d[2]] += u[0]*u[1]*d[2]*mass[i]
            self.grid[index_u[0],index_u[1],index_u[2]] += u[0]*u[1]*u[2]*mass[i]
        self.is_computed = True
        return
    
    def plotSlice(self):
        #TODO
        return

class Chunk(Grid):
    def __init__(self, res, chunk_num):
        super().__init__( res)
        self.combine = 1
        self.chunk_nums = [chunk_num]
        return
    
    def isChunk(self):
        return True
    
    def combine(self, other_chunk):
        self.grid += other_chunk.getGrid()
        self.combine += 1
        self.chunk_nums.extend(other_chunk.chunk_nums)
