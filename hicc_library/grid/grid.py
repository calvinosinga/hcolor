"""
This file defines two grid classes 
"""

import numpy as np
import h5py as hp
import time

class Grid():

    def __init__(self, gridname, res, grid=None):
        if grid is None:
            self.grid = np.zeros((res,res,res), dtype=np.float32)
        else:
            self.grid = grid
        self.in_rss = False
        self.gridname = gridname
        self.is_computed = False
        self.resolution = res
        return
    
    def print(self):       
        print("\n\nprinting the properties of a grid")
        not_print = ["grid"]
        for key,val in self.__dict__.items():
            if key not in not_print:
                print("%s:"%key+str(val))
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
        return self.resolution
    
    def CIC(self, pos, boxsize):
        start = time.time()
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
            self.grid[index_d[0],index_d[1],index_u[2]] += d[0]*d[1]*u[2]
            self.grid[index_d[0],index_u[1],index_d[2]] += d[0]*u[1]*d[2]
            self.grid[index_d[0],index_u[1],index_u[2]] += d[0]*u[1]*u[2]
            self.grid[index_u[0],index_d[1],index_d[2]] += u[0]*d[1]*d[2]
            self.grid[index_u[0],index_d[1],index_u[2]] += u[0]*d[1]*u[2]
            self.grid[index_u[0],index_u[1],index_d[2]] += u[0]*u[1]*d[2]
            self.grid[index_u[0],index_u[1],index_u[2]] += u[0]*u[1]*u[2]
        self.is_computed = True
        self.cic_time = time.time() - start
        return

    def CICW(self, pos, boxsize, mass):
        start = time.time()
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
        self.cicw_time = time.time() - start
        return
    
    
    def saveGrid(self, outfile):
        if self.in_rss:
            grid_save_name = self.gridname+'rs'
        else:
            grid_save_name = self.gridname
        
        dat = outfile.create_dataset(grid_save_name, data=self.grid, compression="gzip", compression_opts=9)
        dct = dat.attrs
        dct["resolution"] = self.resolution
        dct["in_rss"] = self.in_rss
        dct["gridname"] = self.gridname
        if self.is_computed:
            dct["cicw_runtime"] = self.cicw_time
        return dat


class Chunk(Grid):
    def __init__(self, gridname, res, chunk_num, grid=None, combine=1):
        super().__init__(gridname, res, grid)
        self.combine = combine
        if isinstance(chunk_num, list):
            self.chunk_nums = chunk_num
        else:
            self.chunk_nums = [chunk_num]
        return
    
    def isChunk(self):
        return True
    
    def saveGrid(self, outfile):
        dat = super().saveGrid(outfile)
        dat.attrs['chunks'] = self.chunk_nums
        dat.attrs['combine'] = self.combine
        return dat
        
    def combine_chunks(self, other_chunk):
        self.grid += other_chunk.getGrid()
        self.combine += 1
        self.chunk_nums.extend(other_chunk.chunk_nums)
        # TODO: combine cicw runtimes
        return
    
