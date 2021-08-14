"""
This file is responsible for the creation of the contituent sbatch files that make
up the pipeline.
"""
import os
import illustris_python as il

class Sbatch():

    def __init__(self, gd, fieldname, simname, snapshot, axis, resolution):
        # save the input fields
        self.fieldname = fieldname
        self.simname = simname
        self.snapshot = snapshot
        self.axis = axis
        self.resolution = resolution

        # if the field is based on the particle catalog, we need to run combine procedures
        # which makes the making of the sbatch files a bit more complicated
        self.is_ptl = False

        # load number of files
        header = il.groupcat.loadHeader(self.simpath, self.snapshot)
        self.numfiles = header['NumFiles']

        # getting needed paths
        self.sbatch_path = gd['sbatch']
        self.log_path = gd['logs']+self.fieldname+'/'
        self.create_grid_path = gd['create_grid']
        self.combine_path = gd['combine']
        return
    
    def isPtl(self):
        self.is_ptl = True
        return
    
    def makeSbatch(self):
        if self.is_ptl:
            varnames, sbatches, dependencies, savefiles = self._makePtlSbatch()
        else:
            varnames, sbatches, dependencies, savefiles = self._makeCatSbatch()
        return varnames, sbatches, dependencies, savefiles


    # helper methods for subclasses

    def _makePtlSbatch(self):
        # getting basic simulation information - mostly for the number of files
    
        fn = self.fieldname
        # what the names of the sbatch files will be -> returned so that pipeline can use them
        sbatches = ['%s.sbatch'%fn, '%s_combine1.sbatch'%fn, '%s_combine2.sbatch'%fn]

        # the corresponding varnames of those jobs so that the pipeline can match them to the
        # right dependencies
        varnames = ['%sgrid'%fn, '%scombine1'%fn, '%scombine2'%fn]

        # name which jobs depend on another one finishing
        dependencies = {}
        for i in range(len(varnames)-1):
            dependencies[varnames[i+1]] = [varnames[i]]
        grid_mem = self._compute_grid_memory()

        savefiles = self._name_savefiles(varnames, True)

        ###### NOW WRITING SBATCH FILES ##################
        # making the first hiptl sbatch files
        grid_job = open(self.sbatch_path+sbatches[0], 'w')
        grid_dir = self._default_sbatch_settings(fn)
        grid_dir['array']='0-%d'%(self.numfiles-1)
        grid_dir['output']=self.log_path+fn+'%a.log'
        grid_dir['mem-per-cpu']='%d'%grid_mem

        self._sbatch_lines(grid_job, grid_dir)
        idx_name = "$SLURM_ARRAY_TASK_ID"
        grid_cmd_args = (self.create_grid_path, fn, self.simname, self.snapshot, 
                self.axis, self.resolution, idx_name)
        
        self._write_python_line(grid_job, grid_cmd_args)
        
        grid_job.close()
        

        # making the first combine sbatch file
        combine1_job = open(self.sbatch_path+sbatches[1],'w')
        combine1_dir = self._default_sbatch_settings("%s_combine1"%fn)

        combine1_dir['array']='0-%d:20'%(self.numfiles-self.numfiles%20)
        combine1_dir['output']=self.log_path+fn+'_combine1%a.log'
        combine1_dir['mem-per-cpu']='%d'%(grid_mem*2)
        
        self._sbatch_lines(combine1_job, combine1_dir)

        cmd_args = (self.combine_path, fn, idx_name, 
                "$((%s+20))"%idx_name, 1, "%s_combine%s"%(fn,idx_name))
        self._write_python_line(combine1_job, cmd_args)

        combine1_job.close()


        # making the second combine sbatch file
        combine2_job = open(self.sbatch_path+sbatches[2], 'w')
        combine2_dir = self._default_sbatch_settings("%s_combine2"%fn)
        combine2_dir['mem-per-cpu']='%d'%(grid_mem*2)

        self._sbatch_lines(combine2_job, combine2_dir)
        numcombine = int(self.numfiles/20) + 1
        cmd_args = (self.combine_path, "%s_combine"%fn, 0, numcombine,
                1, "%s.hdf5"%fn)
        self._write_python_line(combine2_job, cmd_args)

        combine2_job.close()

        return varnames, sbatches, dependencies, savefiles

    def _makeCatSbatch(self):
        fn = self.fieldname
        sbatches = ['%s.sbatch'%fn]
        varnames = ['%sgrid'%fn]
        dependencies = {}

        gridjob = open(self.sbatch_path+sbatches[0], 'w')
        griddir = self._default_sbatch_settings(fn)
        griddir["mem-per-cpu"] = self._compute_grid_memory()

        self._sbatch_lines(gridjob, griddir)

        cmd_args = self._default_cmd_line(fn)

        self._write_python_line(gridjob, cmd_args)

        gridjob.close()
        return varnames, sbatches, dependencies # get savefiles

    
    def _name_savefiles(self, step_names, has_chunks):
        """
        Returns a formatted savefile name for each step in making the grids. The last formatted string
        is for the chunk, to be given later in the create_grid/combine process
        """
        savefiles = {}
        
        for i in step_names:
            s="%s_%sB_%03dS_%dA_%dR"%(i, self.simname, self.snapshot, self.axis, self.resolution)
            if has_chunks:
                s += ".%s.hdf5"
            else:
                s += ".hdf5"
        
            savefiles[i] = s
        return savefiles

    
    def _default_sbatch_settings(self, jobname):
        sbatch_dir = {}
        sbatch_dir['job-name']=jobname
        sbatch_dir['output']=self.log_path+jobname+'.log'
        sbatch_dir['ntasks']='1'
        sbatch_dir['mail-user']='cosinga@umd.edu'
        sbatch_dir['mail-type']='ALL'
        sbatch_dir['account']='astronomy-hi'
        sbatch_dir['time']='2-1:00:00'
        return sbatch_dir
    
    def _sbatch_lines(self, write_file, sbatch_dir):
        write_file.write("#!/bin/bash\n")
        write_file.write("#SBATCH --share\n")
        write_file.write('#SBATCH --requeue\n')
        keylist = list(sbatch_dir.keys())
        for k in keylist:
            write_file.write('#SBATCH --'+k+'='+str(sbatch_dir[k])+'\n')
        write_file.write('\n')
        return
    
    def _write_python_line(self, write_file, cmdargs=None):
        if cmdargs is None:
            cmdargs = self._default_cmd_line()
        write_file.write("python3")
        for c in cmdargs:
            write_file.write(" "+str(c))
        write_file.write('\n')
        return
    
    def _default_cmd_line(self, name):
        return [self.create_grid_path, name, self.simname, self.snapshot, self.axis, 
                self.resolution]
    
    def _compute_grid_memory(self):
        return int(self.resolution**3/1e6 + 5000)

    def _compute_pk_memory(self):
        return int(self._compute_grid_memory()*2.25)





class hiptl(Sbatch):

    def __init__(self, gd, simname, snapshot, axis, resolution):
        # major class variables
        self.fieldname = 'hiptl'
        self.simname= simname
        self.simpath = gd[simname]
        self.axis = axis
        self.resolution = resolution
        self.snapshot = snapshot

        # loading necessary paths


        return
    
    def makeSbatch(self):

        # getting basic simulation information - mostly for the number of files
        header = il.groupcat.loadHeader(self.simpath, self.snapshot)

        fn = self.fieldname
        # what the names of the sbatch files will be -> returned so that pipeline can use them
        sbatches = ['%s.sbatch'%fn, '%s_combine1.sbatch'%fn, '%s_combine2.sbatch'%fn]

        # the corresponding varnames of those jobs so that the pipeline can match them to the
        # right dependencies
        varnames = ['%sgrid'%fn, '%scombine1'%fn, '%scombine2'%fn]

        # name which jobs depend on another one finishing
        dependencies = {}
        for i in range(len(varnames)-1):
            dependencies[varnames[i+1]] = [varnames[i]]
        grid_mem = self._compute_grid_memory()

        savefiles = self._name_savefiles(varnames, True)

        ###### NOW WRITING SBATCH FILES ##################
        # making the first hiptl sbatch files
        grid_job = open(self.sbatch_path+sbatches[0], 'w')
        grid_dir = self._default_sbatch_settings(fn)
        grid_dir['array']='0-%d'%(header['NumFiles']-1)
        grid_dir['output']=self.log_path+fn+'%a.log'
        grid_dir['mem-per-cpu']='%d'%grid_mem

        self._sbatch_lines(grid_job, grid_dir)
        idx_name = "$SLURM_ARRAY_TASK_ID"
        grid_cmd_args = (self.create_grid_path, fn, self.simname, self.snapshot, 
                self.axis, self.resolution, idx_name)
        
        self._write_python_line(grid_job, grid_cmd_args)
        
        grid_job.close()
        

        # making the first combine sbatch file
        combine1_job = open(self.sbatch_path+sbatches[1],'w')
        combine1_dir = self._default_sbatch_settings("%s_combine1"%fn)

        combine1_dir['array']='0-%d:20'%(header['NumFiles']-header['NumFiles']%20)
        combine1_dir['output']=self.log_path+fn+'_combine1%a.log'
        combine1_dir['mem-per-cpu']='%d'%(grid_mem*2)
        
        self._sbatch_lines(combine1_job, combine1_dir)

        cmd_args = (self.combine_path, fn, idx_name, 
                "$((%s+20))"%idx_name, 1, "%s_combine%s"%(fn,idx_name))
        self._write_python_line(combine1_job, cmd_args)

        combine1_job.close()


        # making the second combine sbatch file
        combine2_job = open(self.sbatch_path+sbatches[2], 'w')
        combine2_dir = self._default_sbatch_settings("%s_combine2"%fn)
        combine2_dir['mem-per-cpu']='%d'%(grid_mem*2)

        self._sbatch_lines(combine2_job, combine2_dir)
        numcombine = int(header['NumFiles']/20) + 1
        cmd_args = (self.combine_path, "%s_combine"%fn, 0, numcombine,
                1, "%s.hdf5"%fn)
        self._write_python_line(combine2_job, cmd_args)

        combine2_job.close()

        return varnames, sbatches, dependencies, savefiles
    


class hisubhalo(Sbatch):
    def __init__(self, gd, simname, snapshot, axis, resolution):
        self.fieldname = 'hisubhalo'
        self.simname = simname
        self.simpath = gd[simname]

        self.snapshot = snapshot

        self.sbatch_path = gd['sbatch']
        self.log_path = gd['logs']+self.fieldname+'/'
        self.axis = axis
        self.resolution = resolution
        self.create_grid_path = gd['create_grid']
        return



class ptl(Sbatch):
    def __init__(self, gd, simname, snapshot, axis, resolution):
        self.fieldname = 'ptl'
        self.simname= simname
        self.simpath = gd[simname]

        self.snapshot = snapshot

        self.sbatch_path = gd['sbatch']
        self.log_path = gd['logs']+self.fieldname+'/'
        self.axis = axis
        self.resolution = resolution
        self.create_grid_path = gd['create_grid']
        self.combine_path = gd['combine']
        return
    
    def makeSbatch(self):

        # getting basic simulation information - mostly for the number of files
        header = il.groupcat.loadHeader(self.simpath, self.snapshot)

        fn = self.fieldname
        # what the names of the sbatch files will be -> returned so that pipeline can use them
        sbatches = ['%s.sbatch'%fn, '%s_combine1.sbatch'%fn, '%s_combine2.sbatch'%fn]

        # the corresponding varnames of those jobs so that the pipeline can match them to the
        # right dependencies
        varnames = ['%sgrid'%fn, '%scombine1'%fn, '%scombine2'%fn]

        # name which jobs depend on another one finishing
        dependencies = {}
        for i in range(len(varnames)-1):
            dependencies[varnames[i+1]] = [varnames[i]]
        grid_mem = self._compute_grid_memory()

        ###### NOW WRITING SBATCH FILES ##################
        # making the first hiptl sbatch files
        grid_job = open(self.sbatch_path+sbatches[0], 'w')
        grid_dir = self._default_sbatch_settings(fn)
        grid_dir['array']='0-%d'%(header['NumFiles']-1)
        grid_dir['output']=self.log_path+fn+'%a.log'
        grid_dir['mem-per-cpu']='%d'%grid_mem

        self._sbatch_lines(grid_job, grid_dir)
        idx_name = "$SLURM_ARRAY_TASK_ID"
        grid_cmd_args = (self.create_grid_path, varnames[0], self.simname, self.snapshot, 
                self.axis, self.resolution, idx_name)
        
        self._write_python_line(grid_job, grid_cmd_args)
        
        grid_job.close()
        

        # making the first combine sbatch file
        combine1_job = open(self.sbatch_path+sbatches[1],'w')
        combine1_dir = self._default_sbatch_settings("%s_combine1"%fn)

        combine1_dir['array']='0-%d:20'%(header['NumFiles']-header['NumFiles']%20)
        combine1_dir['output']=self.log_path+fn+'_combine1%a.log'
        combine1_dir['mem-per-cpu']='%d'%(grid_mem*2)
        
        self._sbatch_lines(combine1_job, combine1_dir)

        cmd_args = (self.combine_path, varnames[0], idx_name, 
                "$((%s+20))"%idx_name, 1, varnames[1])
        self._write_python_line(combine1_job, cmd_args)

        combine1_job.close()


        # making the second combine sbatch file
        combine2_job = open(self.sbatch_path+sbatches[2], 'w')
        combine2_dir = self._default_sbatch_settings("%s_combine2"%fn)
        combine2_dir['mem-per-cpu']='%d'%(grid_mem*2)

        self._sbatch_lines(combine2_job, combine2_dir)
        numcombine = int(header['NumFiles']/20) + 1
        cmd_args = (self.combine_path, varnames[1], 0, numcombine,
                1, varnames[2])
        self._write_python_line(combine2_job, cmd_args)

        combine2_job.close()

        return varnames, sbatches, dependencies

class vn(Sbatch):
    def __init__(self, gd, simname, snapshot, axis, resolution):
        self.fieldname = 'vn'
        self.simname= simname
        self.simpath = gd[simname]

        self.snapshot = snapshot

        self.sbatch_path = gd['sbatch']
        self.log_path = gd['logs']+self.fieldname+'/'
        self.axis = axis
        self.resolution = resolution
        self.create_grid_path = gd['create_grid']
        self.combine_path = gd['combine']
        return
    
    def makeSbatch(self):

        # getting basic simulation information - mostly for the number of files
        header = il.groupcat.loadHeader(self.simpath, self.snapshot)

        fn = self.fieldname
        # what the names of the sbatch files will be -> returned so that pipeline can use them
        sbatches = ['%s.sbatch'%fn, '%s_combine1.sbatch'%fn, '%s_combine2.sbatch'%fn]

        # the corresponding varnames of those jobs so that the pipeline can match them to the
        # right dependencies
        varnames = ['%sgrid'%fn, '%scombine1'%fn, '%scombine2'%fn]

        # name which jobs depend on another one finishing
        dependencies = {}
        for i in range(len(varnames)-1):
            dependencies[varnames[i+1]] = [varnames[i]]
        grid_mem = self._compute_grid_memory()

        ###### NOW WRITING SBATCH FILES ##################
        # making the first hiptl sbatch files
        grid_job = open(self.sbatch_path+sbatches[0], 'w')
        grid_dir = self._default_sbatch_settings(fn)
        grid_dir['array']='0-%d'%(header['NumFiles']-1)
        grid_dir['output']=self.log_path+fn+'%a.log'
        grid_dir['mem-per-cpu']='%d'%grid_mem

        self._sbatch_lines(grid_job, grid_dir)
        idx_name = "$SLURM_ARRAY_TASK_ID"
        grid_cmd_args = (self.create_grid_path, fn, self.simname, self.snapshot, 
                self.axis, self.resolution, idx_name)
        
        self._write_python_line(grid_job, grid_cmd_args)
        
        grid_job.close()
        

        # making the first combine sbatch file
        combine1_job = open(self.sbatch_path+sbatches[1],'w')
        combine1_dir = self._default_sbatch_settings("%s_combine1"%fn)

        combine1_dir['array']='0-%d:20'%(header['NumFiles']-header['NumFiles']%20)
        combine1_dir['output']=self.log_path+fn+'_combine1%a.log'
        combine1_dir['mem-per-cpu']='%d'%(grid_mem*2)
        
        self._sbatch_lines(combine1_job, combine1_dir)

        cmd_args = (self.combine_path, fn, idx_name, 
                "$((%s+20))"%idx_name, 1, "%s_combine%s"%(fn,idx_name))
        self._write_python_line(combine1_job, cmd_args)

        combine1_job.close()


        # making the second combine sbatch file
        combine2_job = open(self.sbatch_path+sbatches[2], 'w')
        combine2_dir = self._default_sbatch_settings("%s_combine2"%fn)
        combine2_dir['mem-per-cpu']='%d'%(grid_mem*2)

        self._sbatch_lines(combine2_job, combine2_dir)
        numcombine = int(header['NumFiles']/20) + 1
        cmd_args = (self.combine_path, "%s_combine"%fn, 0, numcombine,
                1, "%s.hdf5"%fn)
        self._write_python_line(combine2_job, cmd_args)

        combine2_job.close()

        return varnames, sbatches, dependencies

class galaxy(Sbatch):
    def __init__(self, gd, simname, snapshot, axis, resolution):
        self.fieldname = 'galaxy'
        self.simname = simname
        self.simpath = gd[simname]

        self.snapshot = snapshot

        self.sbatch_path = gd['sbatch']
        self.log_path = gd['logs']+self.fieldname+'/'
        self.axis = axis
        self.resolution = resolution
        self.create_grid_path = gd['create_grid']
        return

    def makeSbatch(self):
        fn = self.fieldname
        sbatches = ['%s.sbatch'%fn]
        varnames = ['%sgrid'%fn]
        dependencies = {}

        gridjob = open(self.sbatch_path+sbatches[0], 'w')
        griddir = self._default_sbatch_settings(fn)
        griddir["mem-per-cpu"] = self._compute_grid_memory()

        self._sbatch_lines(gridjob, griddir)

        cmd_args = self._default_cmd_line(fn)

        self._write_python_line(gridjob, cmd_args)

        gridjob.close()
        return varnames, sbatches, dependencies

class nden(Sbatch):
    def __init__(self, gd, simname, snapshot, axis, resolution):
        self.fieldname = 'nden'
        self.simname= simname
        self.simpath = gd[simname]

        self.snapshot = snapshot

        self.sbatch_path = gd['sbatch']
        self.log_path = gd['logs']+self.fieldname+'/'
        self.axis = axis
        self.resolution = resolution
        self.create_grid_path = gd['create_grid']
        self.combine_path = gd['combine']
        return
    
    def makeSbatch(self):

        # getting basic simulation information - mostly for the number of files
        header = il.groupcat.loadHeader(self.simpath, self.snapshot)

        fn = self.fieldname
        # what the names of the sbatch files will be -> returned so that pipeline can use them
        sbatches = ['%s.sbatch'%fn, '%s_combine1.sbatch'%fn, '%s_combine2.sbatch'%fn]

        # the corresponding varnames of those jobs so that the pipeline can match them to the
        # right dependencies
        varnames = ['%sgrid'%fn, '%scombine1'%fn, '%scombine2'%fn]

        # name which jobs depend on another one finishing
        dependencies = {}
        for i in range(len(varnames)-1):
            dependencies[varnames[i+1]] = [varnames[i]]
        grid_mem = self._compute_grid_memory()

        ###### NOW WRITING SBATCH FILES ##################
        # making the first hiptl sbatch files
        grid_job = open(self.sbatch_path+sbatches[0], 'w')
        grid_dir = self._default_sbatch_settings(fn)
        grid_dir['array']='0-%d'%(header['NumFiles']-1)
        grid_dir['output']=self.log_path+fn+'%a.log'
        grid_dir['mem-per-cpu']='%d'%grid_mem

        self._sbatch_lines(grid_job, grid_dir)
        idx_name = "$SLURM_ARRAY_TASK_ID"
        grid_cmd_args = (self.create_grid_path, fn, self.simname, self.snapshot, 
                self.axis, self.resolution, idx_name)
        
        self._write_python_line(grid_job, grid_cmd_args)
        
        grid_job.close()
        

        # making the first combine sbatch file
        combine1_job = open(self.sbatch_path+sbatches[1],'w')
        combine1_dir = self._default_sbatch_settings("%s_combine1"%fn)

        combine1_dir['array']='0-%d:20'%(header['NumFiles']-header['NumFiles']%20)
        combine1_dir['output']=self.log_path+fn+'_combine1%a.log'
        combine1_dir['mem-per-cpu']='%d'%(grid_mem*2)
        
        self._sbatch_lines(combine1_job, combine1_dir)

        cmd_args = (self.combine_path, fn, idx_name, 
                "$((%s+20))"%idx_name, 1, "%s_combine%s"%(fn,idx_name))
        self._write_python_line(combine1_job, cmd_args)

        combine1_job.close()


        # making the second combine sbatch file
        combine2_job = open(self.sbatch_path+sbatches[2], 'w')
        combine2_dir = self._default_sbatch_settings("%s_combine2"%fn)
        combine2_dir['mem-per-cpu']='%d'%(grid_mem*2)

        self._sbatch_lines(combine2_job, combine2_dir)
        numcombine = int(header['NumFiles']/20) + 1
        cmd_args = (self.combine_path, "%s_combine"%fn, 0, numcombine,
                1, "%s.hdf5"%fn)
        self._write_python_line(combine2_job, cmd_args)

        combine2_job.close()

        return varnames, sbatches, dependencies

class dust(Sbatch):
    def __init__(self, gd, simname, snapshot, axis, resolution):
        self.fieldname = 'dust'
        self.simname = simname
        self.simpath = gd[simname]

        self.snapshot = snapshot

        self.sbatch_path = gd['sbatch']
        self.log_path = gd['logs']+self.fieldname+'/'
        self.axis = axis
        self.resolution = resolution
        self.create_grid_path = gd['create_grid']
        return

    def makeSbatch(self):
        fn = self.fieldname
        sbatches = ['%s.sbatch'%fn]
        varnames = ['%sgrid'%fn]
        dependencies = {}

        gridjob = open(self.sbatch_path+sbatches[0], 'w')
        griddir = self._default_sbatch_settings(fn)
        griddir["mem-per-cpu"] = self._compute_grid_memory()

        self._sbatch_lines(gridjob, griddir)

        cmd_args = self._default_cmd_line(fn)

        self._write_python_line(gridjob, cmd_args)

        gridjob.close()
        return varnames, sbatches, dependencies

# class colorptl(Sbatch):
