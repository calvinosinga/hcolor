"""
This file is responsible for the creation of the contituent sbatch files that make
up the pipeline.
"""
import os
import h5py as hp
from hc_lib.fields.galaxy import galaxy
import copy
class Sbatch():

    def __init__(self, gd, fieldname, run_params):
        # save the input fields
        self.fieldname = fieldname
        self.simname = run_params['sim']
        self.snapshot = run_params['snap']
        self.axis = run_params['axis']
        self.resolution = run_params['res']

        # if the field is based on the particle catalog, we need to run combine procedures
        # which makes the making of the sbatch files a bit more complicated
        self.is_ptl = True

        # getting needed paths
        self._load_paths_gd(gd)

        # load number of files
        f = hp.File(gd["load_header"],'r')
        header = dict(f['Header'].attrs)

        self.numfiles = header['NumFilesPerSnapshot']

        return
    
    def isCat(self):
        self.is_ptl = False
        return
    
    def makeSbatch(self):
        if self.is_ptl:
            varnames, sbatches, dependencies, savefiles = self._makePtlSbatch()
        else:
            varnames, sbatches, dependencies, savefiles = self._makeCatSbatch()
        self._makeAutoResultsSbatch(varnames, sbatches, dependencies, savefiles)
        self.varnames = varnames
        self.sbatches = sbatches
        self.dependencies = dependencies
        self.savefiles = savefiles
        return varnames, sbatches, dependencies, savefiles
    
    @staticmethod
    def makeCrossSbatch(first_sbatch, second_sbatch):
        fn1 = first_sbatch.fieldname
        fn2 = second_sbatch.fieldname

        cross_sbatch_file = ["%sX%s.sbatch"%(fn1, fn2)]
        cross_var_name = ["%sX%s"%(fn1, fn2)]
        cross_savefile = {}
        cross_savefile[cross_var_name[0]] = \
                first_sbatch._get_base_name("%sX%s"%(fn1, fn2))+'.pkl'

        # the cross results depend on the last job from each field
        last_jobs = [second_sbatch.varnames[-2], first_sbatch.varnames[-2]]
        dependency = {}
        dependency[cross_var_name[0]] = last_jobs

        crossjob = open(first_sbatch.sbatch_path + cross_sbatch_file[0], 'w')

        crossdir = first_sbatch._default_sbatch_settings(cross_var_name[0])
        crossdir['mem-per-cpu'] = first_sbatch._compute_xpk_memory()
        first_sbatch._sbatch_lines(crossjob, crossdir)

        cmd_args = [first_sbatch.cross_path, last_jobs[0], last_jobs[1]]
        
        first_sbatch._write_python_line(crossjob, cmd_args)

        crossjob.close()
        return cross_var_name, cross_sbatch_file, dependency, cross_savefile
    # helper methods

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

        savefiles = self._name_savefiles(varnames)

        ###### NOW WRITING SBATCH FILES ##################
        # making the first hiptl sbatch files
        grid_job = open(self.sbatch_path+sbatches[0], 'w')
        grid_dir = self._default_sbatch_settings(fn)
        grid_dir['array']='0-%d'%(self.numfiles-1)
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

        combine1_dir['array']='0-%d:20'%(self.numfiles-self.numfiles%20)
        combine1_dir['output']=self.log_path+fn+'_combine1_%a.log'
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
        cmd_args = (self.combine_path, varnames[1], 0, self.numfiles,
                20, varnames[2])
        self._write_python_line(combine2_job, cmd_args)

        combine2_job.close()

        return varnames, sbatches, dependencies, savefiles

    def _makeCatSbatch(self):
        fn = self.fieldname

        sbatches = ['%s.sbatch'%fn]

        varnames = ['%sgrid'%fn]

        dependencies = {}

        savefiles = self._name_savefiles(varnames)

        gridjob = open(self.sbatch_path+sbatches[0], 'w')
        griddir = self._default_sbatch_settings(fn)
        griddir["mem-per-cpu"] = self._compute_grid_memory()

        self._sbatch_lines(gridjob, griddir)

        cmd_args = self._default_cmd_line(varnames[0])

        self._write_python_line(gridjob, cmd_args)

        gridjob.close()
        return varnames, sbatches, dependencies, savefiles

    def _makeAutoResultsSbatch(self, varnames, sbatches, dependencies, savefiles):
        auto_sbatch_file = "%s_auto.sbatch"%self.fieldname
        auto_var_name = "%s_auto"%self.fieldname

        dependencies[auto_var_name] = [varnames[-1]]
        sbatches.append(auto_sbatch_file)
        varnames.append(auto_var_name)
 

        resjob = open(self.sbatch_path + auto_sbatch_file, 'w')

        resdir = self._default_sbatch_settings(auto_var_name)
        resdir['mem-per-cpu'] = self._compute_pk_memory()
        self._sbatch_lines(resjob, resdir)

        cmd_args = [self.auto_results_path, dependencies[auto_var_name][0]]
        self._write_python_line(resjob, cmd_args)

        resjob.close()
        return


    def _name_savefiles(self, step_names):
        """
        Returns a formatted savefile name for each step in making the grids. The last formatted string
        is for the chunk, to be given later in the create_grid/combine process
        """
        savefiles = {}
        
        for i in step_names:
            base=self._get_base_name(i)
            if self.is_ptl:
                s = base+ ".%d.hdf5"
            else:
                s =base + ".hdf5"
        
            savefiles[i] = s
        savefiles[step_names[-1]] = base+".hdf5"
        # the last combine file shouldn't have a chunk formatting in it
        return savefiles

    def _get_base_name(self, name):
        return "%s_%sB_%03dS_%dA_%dR"%(name, self.simname, self.snapshot, self.axis, self.resolution)
    
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
    
    def _load_paths_gd(self, gd):
        self.cross_path = gd['cross_result']
        self.sbatch_path = gd['sbatch']
        self.log_path = gd['logs']+self.fieldname+'/'
        self.create_grid_path = gd['create_grid']
        self.combine_path = gd['combine']
        self.simpath = gd["load_header"]
        self.auto_results_path = gd["auto_result"]
        return
    
    def _default_cmd_line(self, name):
        return [self.create_grid_path, name, self.simname, self.snapshot, self.axis, 
                self.resolution]
    
    def _compute_grid_memory(self):
        return int(self.resolution**3/1e6 * 4 + 7000)

    def _compute_pk_memory(self):
        return int(self._compute_grid_memory()*2.25 + 10000)
    
    def _compute_xpk_memory(self):
        return int(self._compute_grid_memory() * 2.25**2)

