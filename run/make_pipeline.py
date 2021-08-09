"""
This script accepts command-line inputs and creates a directory to store output, and creates a pipeline that it then submits.
It depends on there being an implementation of the runs given within this folder, in the respective [run_name].py.
"""
import sys
import os
import numpy as np
import h5py as hp
from numpy.core.fromnumeric import var
from hicc_library.sbatch.sbatch import Sbatch

SIMNAME = sys.argv.pop(1)
SNAPSHOT = int(sys.argv.pop(1))
AXIS = int(sys.argv.pop(1))
RESOLUTION = int(sys.argv.pop(1))

sys.argv.pop(0) # removing unneeded script name

RUNNAMES = sys.argv


print("simulation name: %s"%SIMNAME)
print("snapshot: %03d"%SNAPSHOT)
print("axis: %d"%AXIS)
print("resolution of grid: %d"%RESOLUTION)
print("runs given: "+str(RUNNAMES))

# defining basic path names: adjust paths here
LSTR = '/lustre/cosinga/'
HIH2 = '/lustre/diemer/illustris/hih2/'
HCOLOR = LSTR + 'hcolor/'
# this directory stores the basic paths that will be used throughout the run
paths = {}

paths[SIMNAME] = LSTR+'%s/'%SIMNAME
paths['output'] = LSTR+'hcolor/output/'
paths['output'] = paths['output']+'hicc_%sB_%03dS_%dR_'%(SIMNAME, SNAPSHOT, RESOLUTION)
paths['snapshot'] = paths[SIMNAME]+'/snapdir_%03d/'%(SNAPSHOT)
paths['load_header'] = paths['snapshot']+'snap_%03d.0.hdf5'
paths['create_grid'] = HCOLOR + 'run/create_grid.py'
paths['combine'] = HCOLOR + 'run/combine.py'
# create output directory
for i in range(25):
    if not os.path.isdir(paths['output']+str(i)):
        os.mkdir(paths['output']+str(i)+'/')
        paths['output'] = paths['output']+str(i)+'/'
        break

# create subdirectories: 
def create_subdirectory(subdir, savepath=True):
    os.mkdir(paths['output']+subdir+'/')
    splt = subdir.split("/")
    # make sure they aren't saving over other paths
    if not savepath:
        paths[splt[-1]] = paths['output']+subdir+'/'
    return

create_subdirectory("grids")
create_subdirectory("slices")
create_subdirectory("sbatch")
create_subdirectory("sbatch/logs")
create_subdirectory("results")
create_subdirectory("results/plots")

for i in RUNNAMES:
    create_subdirectory("results/plots/"+i,False)
    create_subdirectory("slices/"+i, False)
    create_subdirectory("sbatch/logs/"+i, False)

# getting the properties of the runs given

fields = []
for i in RUNNAMES:
    fields.append(Sbatch(paths, i, SIMNAME, SNAPSHOT, AXIS, RESOLUTION))
    
# letting the Fields object create the individual sbatch files, saving the output to put into pipeline
dependencies={}
jobnames = []
varnames = []
for f in fields:
    svars, sjobs, sdeps = f.makeSbatch()
    jobnames.extend(sjobs)
    dependencies.update(sdeps)
    varnames.extend(svars)

# create pk sbatch files

# save paths here
print("the path dictionary:")
print(paths)
pathpath = paths['output']+'paths.hdf5'
w_path = hp.File(pathpath, 'w')
klist = list(paths.keys())
for key in klist:
    w_path.create_dataset(key, data=paths[key])


# add hih2 hiptl, tng snapshot, postprocessing files to path,
# creating the pipeline
pipe = open(paths['output']+'sbatch/pipeline.bash', 'w')

pipe.write("#!/bin/bash\n")
pipe.write("PATHFILE=%s\n"%pathpath)

# helper method to write jobs and their dependencies
def write_line(varname, sname, jdep=None):
    if jdep is None:
        pipe.write("$%s=(sbatch --export=ALL,PATHFILE=$PATHFILE %s)\n\n"%(varname, sname))
    else:
        pipe.write("$%s=(sbatch --export=ALL,PATHFILE=$PATHFILE --dependency=afterok:"%varname)
        for i in range(len(jdep)):
            if not jdep[i] == jdep[-1]:
                pipe.write('$'+jdep[i]+':')
            else:
                pipe.write('$'+jdep[i])
        pipe.write(" %s\n"%sname)
    pipe.write("%s=\"${%s##* }\"\n\n"%(varname, varname))
    return

for i in range(len(jobnames)):
    try:
        write_line(varnames[i], jobnames[i], dependencies[varnames[i]])
    except KeyError:
        write_line(varnames[i], jobnames[i])

