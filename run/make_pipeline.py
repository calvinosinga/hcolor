"""
This script accepts command-line inputs and creates a directory to store output, and creates a pipeline that it then submits.
It depends on there being an implementation of the runs given within this folder, in the respective [run_name].py.
"""
import sys
import os
import numpy as np
import h5py as hp
from hicc_library.sbatch.sbatch import Sbatch


SIMNAME = sys.argv.pop(1)
SNAPSHOT = int(sys.argv.pop(1))
RESOLUTION = int(sys.argv.pop(1))
sys.argv.pop(0) # removing unneeded script name

RUNNAMES = sys.argv


print("simulation name: %s"%SIMNAME)
print("snapshot: %03d"%SNAPSHOT)
print("resolution of grid: %d"%RESOLUTION)
print("runs given: "+str(RUNNAMES))

# defining basic path names: adjust paths here
LSTR = '/lustre/cosinga/'
HIH2 = '/lustre/diemer/illustris/hih2/'

# this directory stores the basic paths that will be used throughout the run
paths = {}

paths[SIMNAME] = LSTR+'%s/'%SIMNAME
paths['output'] = LSTR+'hcolor/output/'
paths['output'] = paths['output']+'hicc_%sB_%03dS_%dR_'%(SIMNAME, SNAPSHOT, RESOLUTION)


# create output directory
for i in range(25):
    if not os.path.isdir(paths['output']+str(i)):
        os.mkdir(paths['output']+str(i)+'/')
        paths['output'] = paths['output']+str(i)+'/'
        break

# create subdirectories: 
def create_subdirectory(subdir):
    os.mkdir(paths['output']+subdir+'/')
    splt = subdir.split("/")
    paths[splt[-1]] = paths['output']+subdir+'/'
    return

create_subdirectory("fields")
create_subdirectory("slices")
create_subdirectory("sbatch")
create_subdirectory("sbatch/logs")
create_subdirectory("results")
create_subdirectory("results/plots")

for i in RUNNAMES:
    create_subdirectory("results/plots/"+i+"/")

# getting the properties of the runs given

fields = []
for i in RUNNAMES:
    fields.append(Sbatch(paths, i, SIMNAME, SNAPSHOT))
    
# letting the Fields object create the individual sbatch files, saving the output to put into pipeline
lines=[]
for f in fields:
    lines.append(f.makeSbatch(paths['output']+"sbatch/", SIMNAME, SNAPSHOT, RESOLUTION))

# create pk sbatch files

# save paths here

# creating the pipeline
pipe = open(paths['output']+'sbatch/pipeline.bash')
