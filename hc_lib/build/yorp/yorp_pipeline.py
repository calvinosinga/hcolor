#!/usr/bin/env python3
import pickle as pkl
from hc_lib.build.gd import IODict
from hc_lib.build.input import Input
from hc_lib.build.yorp.job import JobManager
import h5py as hp
import os

OUTPATH = '/yorp08a/cosinga/'
TNGPATH = '/net/nyx/nyx1/diemer/illustris/'
HCOLOR = '/home/cosinga/hcolor/'

tng_dict = {'tng100':'L75n1820TNG', 'tng300':'L205n2500TNG',
        'tng100-2':'L75n910TNG', 'tng100-3':'L75n455TNG', 
        'tng50':'L35n2160TNG'}
    
def main():
    ioobj = Input()
    runs = ioobj.getRuns()
    rp = ioobj.getParams()

    gdobj = IODict(rp, runs, OUTPATH, TNGPATH+tng_dict[rp['sim']]+'/output/', HCOLOR)
    gd = gdobj.getGlobalDict()
    pd = gdobj.getPathDict()


    prefix = rp['prefix']
    # load number of files
    f = hp.File(gd["load_header"],'r')
    header = dict(f['Header'].attrs)

    numfiles = header['NumFilesPerSnapshot']
    jman = JobManager()
    
    for r in runs:
        if ioobj.isPtl(r):
            jman.addPtlJobs(r, numfiles, pd)
        if ioobj.isCat(r):
            jman.addCatJobs(r, pd, gd, rp)


    print('global dict:')
    print(gd)

    print('\n\npath dict:')
    print(pd)

    pkl.dump(jman, open(prefix+'_job_manager.pkl', 'wb'), pkl.HIGHEST_PROTOCOL)
    pkl.dump(gd, open(pd['output']+'gd.pkl', 'wb'), pkl.HIGHEST_PROTOCOL)
    os.environ['GDFILE'] = pd['output'] + 'gd.pkl'
    return

main()
