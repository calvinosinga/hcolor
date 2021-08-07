"""
This file is responsible for the creation of the contituent sbatch files that make
up the pipeline.
"""
import os
import illustris_python as il

class Sbatch():

    def __init__(self, paths, fieldname, simname, snapshot):
        if fieldname == 'hiptl':
            self.field = hiptl(paths, simname, snapshot)
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
    
    def makeSbatch(self):
        self.field.makeSbatch()
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



class hiptl(Sbatch):

    def __init__(self, paths, simname, snapshot):
        self.simpath = paths[simname]
        self.snapshot = snapshot
        self.sbatch_path = paths['sbatch']
        return
    
    def makeSbatch(self):


        # getting basic simulation information - mostly for the number of files
        header = il.groupcat.loadHeader(self.simpath, self.snapshot)

        grid_mem = self._compute_grid_memory()
        # making the first hiptl sbatch files
        grid_job = open(self.sbatch_path+'hiptl.sbatch', 'w')
        grid_dir = self._default_sbatch_settings('hiptl')
        grid_dir['array']='0-%d'%(header['NumFiles']-1)
        grid_dir['output']='logs/hiptl%a.log'
        grid_dir['mem-per-cpu']='%d'%grid_mem

        self._sbatch_lines(grid_job,grid_dir)

        #TODO: write python lines

        grid_job.close()
        
        # making the first combine sbatch file
        combine1_job = open(self.sbatch_path+'hiptl_combine1.sbatch','w')
        combine1_dir = self._default_sbatch_settings("hiptl_combine1")
        combine1_dir['array']='0-%d:20'%(header['NumFiles']-header['NumFiles']%20)
        combine1_dir['output']='logs/hiptl_combine1%a.log'
        combine1_dir['mem-per-cpu']='%d'%(grid_mem*2)
        
        self._sbatch_lines(combine1_job, combine1_dir)

        #TODO write python lines

        combine1_job.close()

        # making the second combine sbatch file
        combine2_job = open(self.sbatch_path+'hiptl_combine2.sbatch', 'w')
        combine2_dir = self._default_sbatch_settings("hiptl_combine2")
        combine2_dir['mem-per-cpu']='%d'%(grid_mem*2)

        self._sbatch_lines(combine2_job, combine2_dir)

        #TODO: write python lines

        combine2_job.close()

        #TODO: return line to add to pipeline
        return

# class hisubhalo(Field):
#     def __init__(self, name):
#         super().__init__(name)

# class ptl(Field):
#     def __init__(self, name):
#         super().__init__(name)

# class vn(Field):
#     def __init__(self, name):
#         super().__init__(name)

# class galaxy(Field):
#     def __init__(self, name):
#         super().__init__(name)