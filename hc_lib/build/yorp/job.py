#!/usr/bin/env python3

class Job():
    def __init__(self, fieldname, run_script_name, cmdargs):
        self.fn = fieldname
        self.rsn = run_script_name
        self.args = cmdargs
        self.dependencies = []
        
        return

    def addDep(self, dep_job):
        if isinstance(dep_job, list):
            for dj in range(len(dep_job)):
                dep_jobID = dep_job[dj].getJobName()
                self.dependencies.append(dep_jobID)
        else:
            dep_jobID = dep_job.getJobName()
            self.dependencies.append(dep_jobID)
        return
    
    def setCmd(self, args):
        self.args = args
        return

    def getCmd(self):
        return self.args
    
    def getRunScriptName(self):
        return self.rsn

    def getJobName(self):
        return "%s_%s"%(self.fn, self.rsn)
    
    def getPklName(self, run_params):
        rp = run_params
        path = "%s_%sB_%03dS_%dA_%dR.pkl"%(self.fn, rp['sim'], rp['snap'], rp['axis'], rp['res'])
        return path

    def getHdf5GridName(self, run_params):
        rp = run_params
        path = "%s_%sB_%03dS_%dA_%dR.hdf5"%(self.getJobName(), rp['sim'], rp['snap'], rp['axis'], rp['res'])
        return path
    
    def getDep(self):
        return self.dependencies

class JobManager():
    def __init__(self):
        self.jlist = [] # need a jlist that later gets tranformed into a queue because
        # I can't
        return
    
    #TODO: create cross jobs
    def addPtlJobs(self, fieldname, path_dict, global_dict, run_params):
        rp = run_params
        pd = path_dict
        gd = global_dict
        nfiles = rp['nfiles']
        # define the command line arguments for the three processes
        
        create_args = ['python3',pd['create_grid'], fieldname, rp['sim'], rp['snap'],
                rp['axis'], rp['res']]
        combine_args = ['python3', pd['combine']]
        auto_args = ['python3', pd['auto_result']]

        # make the create_grid jobs
        createJoblist = []
        for i in range(nfiles):
            createJoblist.append(Job(fieldname, 'create.%d'%(i), create_args))
        self.jlist.extend(createJoblist)

        # make the combine jobs
        do_two_combines = nfiles > 20
        combineJoblist = []
        for i in range(0, nfiles, 20):
            ijob = Job(fieldname, 'combine1.%d'%(i), combine_args)
            ijob.addDep(createJoblist)
            combineJoblist.append(ijob)
        self.jlist.extend(combineJoblist)
        if do_two_combines:
            combine2_args = [] #TODO define combine2 args
            c2job = Job(fieldname, "combine2", combine2_args)
            c2job.addDep(combineJoblist)
            self.jlist.append(c2job)
        
        # make the auto pk jobs
        autoJob = Job(fieldname, "auto", auto_args)
        if do_two_combines:
            autoJob.addDep(c2job)
        else:
            autoJob.addDep(combineJoblist)
        
        return


    def addCatJobs(self, fieldname, path_dict, global_dict, run_params):
        pd = path_dict
        rp = run_params
        gd = global_dict
        # define the command line arguments for the two processes
        
        create_args = ['python3',pd['create_grid'], fieldname, rp['sim'], rp['snap'],
                rp['axis'], rp['res']]
        auto_args = ['python3', pd['auto_result']]

        createJob = Job(fieldname, "create", create_args)
        self.jlist.append(createJob)
        
        # where the grid for the create job is saved
        auto_args.append(pd['grids'] + createJob.getHdf5GridName(rp))

        autoJob = Job(fieldname, "auto", auto_args)
        autoJob.addDep(createJob)
        self.jlist.append(autoJob)

        # now adding pickle to gd
        gd['pickles'][fieldname] = pd['results'] + autoJob.getPklName(rp)
        return
    
    def _getJob(self, jobname):
        for j in self.jlist:
            if jobname == j.getJobName():
                return j
        return None
    
    def _addRoot(self, job, queue):
        if not job.getDep() and job not in queue:
            queue.append(job)
            return
        elif job in queue:
            return
        else:
            depList = job.getDep()
            for dj in depList:
                djob = self._getJob(dj)
                self._addRoot(djob, queue)
            queue.append(job)
            return
        

    def getQueue(self):
        queue = []
        for j in range(len(self.jlist)):
            self._addRoot(self.jlist[j], queue)
                
        return queue




    
    
