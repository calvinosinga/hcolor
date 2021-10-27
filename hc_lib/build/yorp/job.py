import h5py as hp


class Job():
    def __init__(self, jobID, command, cmdargs):
        self.id = jobID
        self.cmd = command
        self.args = cmdargs
        self.dependencies = []
        
        return

    def addDep(self, dep):
        self.dependencies.append(dep)
        return
    
    def line(self):
        return

def makePtlJobs(name, nfiles, gd, pd):
    createJoblist = []
    createCmd = 'python3 %s'%pd['create_grid']
    combineCmd = 'python3 %s'%pd['combine']
    autoCmd = 'python3 %s'%pd['auto_result']
    # make the create_grid jobs
    for i in range(nfiles):
        createJoblist.append(Job('%s_create%d'%(name,i), createCmd))
    
    combineJoblist = []
    for i in range(0, nfiles, 20):
        combineJoblist.append(Job('%s_combine'))

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



    
    