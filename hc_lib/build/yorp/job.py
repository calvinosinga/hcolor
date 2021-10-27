#!/usr/bin/env python3
import h5py as hp


class Job():
    def __init__(self, fieldname, jobID, cmdargs):
        self.fn = fieldname
        self.id = jobID
        self.args = cmdargs
        self.dependencies = []
        
        return

    def addDep(self, dep_job):
        if isinstance(dep_job, list):
            for dj in dep_job:
                dep_jobID = dj.getID()
                self.dependencies.append(dep_jobID)
        else:
            dep_jobID = dep_job.getID()
            self.dependencies.append(dep_jobID)
        return
    
    def getJobName(self):
        return "%s_%s"%(self.fn, self.id)

    # check when to add Cross Jobs?
    def getCmd(self):
        return

class JobManager():
    def __init__(self):
        self.jlist = []
        return
    

    def addPtlJobs(self, fieldname, nfiles, pd):
        # define the command line arguments for the three processes
        #TODO fill out the rest of the cmd line arguments
        create_args = ['python3',pd['create_grid']]
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
        #TODO check if this creates the right number of jobs
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

    def addCatJobs(self, fieldname, pd):
        # define the command line arguments for the two processes
        #TODO fill out the rest of the cmd line arguments
        create_args = ['python3',pd['create_grid']]
        auto_args = ['python3', pd['auto_result']]

        createJob = Job(fieldname, "create", create_args)
        self.jlist.append(createJob)

        autoJob = Job(fieldname, "auto", auto_args)
        autoJob.addDep(createJob)
        self.jlist.append(createJob)
        return
    

    def getQueue(): #TODO turn the job list into organized queue
        return
    
def makeJobs(ioobj, gd, pd):
    runs = ioobj.getRuns()
    rp = ioobj.getParams()

    # load number of files
    f = hp.File(gd["load_header"],'r')
    header = dict(f['Header'].attrs)

    numfiles = header['NumFilesPerSnapshot']
    jobs = []
    for r in range(len(runs)):
        # if this field is based on particle catalog...
        if ioobj.isPtl(runs[r]):



    
    
