"""
This file defines two grid classes 
"""

import numpy as np
import h5py as hp
import time

from numpy.lib.function_base import trim_zeros

class Grid():

    def __init__(self, gridname, res, grid=None, verbose=False):
        if grid is None:
            self.is_computed = False
            self.grid = np.zeros((res,res,res), dtype=np.float32)
        else:
            self.grid = grid
            self.is_computed = True
            
        self.in_rss = False
        self.gridname = gridname
        self.ignore = False
        self.combine = -1 # not intended for combination (see chunk)
        self.resolution = res
        self.mas_runtime = 0
        self.v = verbose
        return
    
    def print(self):       
        print("printing the properties of a grid")
        not_print = ["grid"]
        for key,val in self.__dict__.items():
            if key not in not_print:
                print("%s:"%key+str(val))
        print("grid_sum: %f"%np.sum(self.grid))
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
        self.mas_runtime = time.time() - start
        return

    def CICW(self, pos, boxsize, mass):
        if self.v:
            print("\tstarting CICW in grid.py...")
            print("\tposition example:" + str(pos[0]))
            print("\tcumulative mass: "+ str(np.sum(mass)))
            print("\tboxsize given: "+str(boxsize))
            print("\tboxsize must be Mpc/h")

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
        self.mas_runtime = time.time() - start
        if self.v:
            print("finished CICW")
            print("grid sum: "+str(np.sum(self.grid)))
        return
    
    def ignoreGrid(self):
        self.ignore = True
        return
    
    def saveGrid(self, outfile):
        if self.in_rss:
            grid_save_name = self.gridname+'rs'
        else:
            grid_save_name = self.gridname
        
        dat = outfile.create_dataset(grid_save_name, data=self.grid, 
                compression="gzip", compression_opts=9)
        
        dct = dat.attrs
        dct["resolution"] = self.resolution
        dct["in_rss"] = self.in_rss
        dct["gridname"] = self.gridname
        dct["ignore"] = self.ignore
        dct["combine"] = self.combine
        if self.is_computed:
            dct["mas_runtime"] = self.mas_runtime
        return dat
    
    @classmethod
    def loadGrid(cls, dataset, verbose=False):
        dct = dict(dataset.attrs)
        grid = Grid(dct['gridname'], dct['resolution'], dataset[:])
        grid.mas_runtime = dct['mas_runtime']
        grid.ignore = dct['ignore']
        grid.in_rss = dct['in_rss']
        grid.is_computed = True
        return grid
    
        
class Chunk(Grid):
    def __init__(self, gridname, res, chunk_num, grid=None, verbose=False):
        super().__init__(gridname, res, grid, verbose)
        self.combine = 1
        self.mas_runtime = 0
        self.chunk_nums = [chunk_num]
        return
    
    def isChunk(self):
        return True
    
    def saveGrid(self, outfile):
        dat = super().saveGrid(outfile)
        dat.attrs['chunks'] = self.chunk_nums
        return dat
        
    def combineChunks(self, other_chunk):
        if self.v:
            print("\n\nstarting combine procedure...")
            print("self chunk:")
            self.print()
            print("other chunk:")
            other_chunk.print()
        
        self.grid += other_chunk.getGrid()
        self.combine += 1
        self.chunk_nums.extend(list(other_chunk.chunk_nums))
        self.mas_runtime += other_chunk.mas_runtime
        if self.v:
            print("finished combine. Resulting grid\'s properties:")
            self.print()

        return

    @classmethod
    def loadGrid(cls, dataset, verbose=False):
        dct = dict(dataset.attrs)
        grid = Chunk(dct['gridname'], dct['resolution'], 0, dataset[:], verbose=verbose)
        grid.in_rss = dct['in_rss']
        grid.ignore = dct['ignore']
        grid.is_computed = True
        grid.mas_runtime = dct['mas_runtime']
        grid.combine = dct['combine']
        grid.chunk_nums = list(dct['chunks'])
        return grid
