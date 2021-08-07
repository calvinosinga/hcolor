"""
This file is responsible for the creation of the contituent sbatch files that make
up the pipeline.
"""
import os
from hicc_library.paths import getPaths
from hicc_library.fields.hiptl import hiptl

class Field():

    def __init__(self, paths, fieldname, simname = '', snapshot = 0, resolution = 0, chunk = 0):
        if fieldname == 'hiptl':
            self.field = hiptl(simname, snapshot, resolution, chunk)
        elif fieldname == 'hisubhalo':
            self.field = hisubhalo()
        elif fieldname == 'ptl':
            self.field = ptl()
        elif fieldname == 'vn':
            self.field = vn()
        elif fieldname == 'galaxy':
            self.field = galaxy()
        else:
            raise NotImplementedError("there is no field named %s"%fieldname)
        return
    
    def makeSbatch(self, path):
        self.field.makeSbatch(path)
        return
    
    
    def computeGrids(self):
        self.field.computeGrids()
        return
    
    def saveGrids(self):
        self.field.saveGrids()
        return
    
    def computePk(self):
        self.field.computePk()
        return
    
    def computeCorr(self):
        self.field.computeCorr()
        return
    
    # helper methods for subclasses
    def _default_sbatch_settings(self, jobname):
        sbatch_dir = {}
        sbatch_dir['job-name']=jobname
        sbatch_dir['output']='logs/'+jobname+'.log'
        sbatch_dir['ntasks']='1'
        sbatch_dir['mail-user']='cosinga@umd.edu'
        sbatch_dir['mail-type']='ALL'
        sbatch_dir['account']='astronomy-hi'
        sbatch_dir['time']='2-1:00:00'
        return sbatch_dir
    
    def _sbatch_lines(self, write_file, sbatch_dir):
        write_file.write("#!/bin/bash\n")
        write_file.write("#SBATCH --share\n")
        keylist = list(sbatch_dir.keys())
        for k in keylist:
            write_file.write('#SBATCH --'+k+'='+sbatch_dir[k]+'\n')
        return
    
    def _compute_grid_memory(self):
        return int(self.field.res**3/1e6 + 5000)

    def _compute_pk_memory(self):
        return int(self._compute_grid_memory()*2.25)





class hisubhalo(Field):
    def __init__(self, name):
        super().__init__(name)

class ptl(Field):
    def __init__(self, name):
        super().__init__(name)

class vn(Field):
    def __init__(self, name):
        super().__init__(name)

class galaxy(Field):
    def __init__(self, name):
        super().__init__(name)