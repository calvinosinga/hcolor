"""
This script accepts command-line inputs and creates a directory to store output, and creates a pipeline that it then submits.
It depends on there being an implementation of the runs given within this folder, in the respective [run_name].py.
"""
import sys
import os
import numpy as np
import h5py as hp
from sbatch import Sbatch
import pickle as pkl

PREFIX = sys.argv.pop(1)
SIMNAME = sys.argv.pop(1)
SNAPSHOT = int(sys.argv.pop(1))
AXIS = int(sys.argv.pop(1))
RESOLUTION = int(sys.argv.pop(1))

sys.argv.pop(0) # removing unneeded script name

RUNNAMES = sys.argv

VERBOSE = int(input("how verbose should the logs be? (0 for limited, 1 for detailed)"))
implemented_fields = ['hiptl', 'hisubhalo', 'galaxy', 'galaxy_dust', 'vn', 'galaxy_ptl', 'ptl']
HI_fields = ['hiptl', 'hisubhalo', 'vn']
matter_fields = ['galaxy','galaxy_dust', 'galaxy_ptl']

print("output directory prefix:%s"%PREFIX)
print("verbosity:%d"%VERBOSE)
print("simulation name: %s"%SIMNAME)
print("snapshot: %03d"%SNAPSHOT)
print("axis: %d"%AXIS)
print("resolution of grid: %d"%RESOLUTION)
print("runs given: "+str(RUNNAMES))
print("currently implemented fields: "+ str(implemented_fields))


# this is the global dictionaries that stores paths and some user input,
# like verbosity
gd = {}
LSTR = '/lustre/cosinga/'
HIH2 = '/lustre/diemer/illustris/hih2/'
HCOLOR = LSTR + 'hcolor/'

gd['verbose']=VERBOSE
gd[SIMNAME] = LSTR+'%s/'%SIMNAME
gd['output'] = LSTR+'hcolor/output/'
gd['output'] = gd['output']+'%s_%sB_%03dS_%dA_%dR'%(PREFIX, SIMNAME, SNAPSHOT, AXIS, RESOLUTION)
gd['snapshot'] = gd[SIMNAME]+'snapdir_%03d/snap_%03d.'%(SNAPSHOT,SNAPSHOT) + "%d.hdf5" # chunks are given in fields subclasses
gd['load_header'] = gd['snapshot']%(0)
gd['create_grid'] = HCOLOR + 'run/create_grid.py'
gd['combine'] = HCOLOR + 'run/combine.py'
gd['hih2ptl'] = HIH2 + "hih2_particles_%03d"%SNAPSHOT + ".%d.hdf5"
gd['post'] = gd[SIMNAME]+'postprocessing/'
gd['dust'] = gd['post']+'stellar_light/'+ \
        'Subhalo_StellarPhot_p07c_cf00dust_res_conv_ns1_rad30pkpc_%03d.hdf5'%SNAPSHOT
gd['auto_result'] = HCOLOR+'run/auto.py'
gd['cross_result'] = HCOLOR+'run/cross.py'
gd['hih2catsh'] = gd['post']+'hih2_galaxy_%03d.hdf5'%SNAPSHOT
gd['TREECOOL'] = gd[SIMNAME]+'TREECOOL_fg_dec11'
# prompting user for other needed input
isptl = {}
for r in RUNNAMES:
    usrval = int(input("does %s use the particle catalog? (1=yes,0=no)"%r))
    if not usrval in (0,1):
        raise ValueError("invalid input, must be 1 or 0")
    isptl[r] = usrval

# create output directory
if not os.path.isdir(gd['output']+'/'):
    os.mkdir(gd['output']+'/')
    gd['output'] = gd['output'] + '/'


# create subdirectories: 
def create_subdirectory(subdir, savepath=True):
    os.mkdir(gd['output']+subdir+'/')
    splt = subdir.split("/")
    # make sure they aren't saving over other paths
    if savepath:
        gd[splt[-1]] = gd['output']+subdir+'/'
    return

create_subdirectory("grids")
create_subdirectory("sbatch")
create_subdirectory("sbatch/logs")
create_subdirectory("results")
create_subdirectory("results/plots")

for i in RUNNAMES:
    create_subdirectory("results/plots/"+i,False)
    create_subdirectory("sbatch/logs/"+i, False)

# getting the properties of the runs given

fields = []
for i in RUNNAMES:
    fields.append(Sbatch(gd, i, SIMNAME, SNAPSHOT, AXIS, RESOLUTION))
    
# letting the Fields object create the individual sbatch files, saving the output to put into pipeline
dependencies={}
jobnames = []
varnames = []
savefiles = {}
for f in range(len(fields)):
    if not isptl[RUNNAMES[f]]:
        fields[f].isCat()

    svars, sjobs, sdeps, ssave = fields[f].makeSbatch()
    jobnames.extend(sjobs)
    dependencies.update(sdeps)
    varnames.extend(svars)
    savefiles.update(ssave)

for i in range(len(fields)):
    for j in range(len(fields)):
        fn1 = fields[i].fieldname
        fn2 = fields[j].fieldname
        if fn1 in HI_fields and fn2 in matter_fields:
            xplotpath = gd['plots'] + '%sX%s/'%(fn1,fn2)
            os.mkdir(xplotpath)
            xplotkey = '%sX%s_plots'%(fn1,fn2)
            gd[xplotkey]=xplotpath
            cvar, csb, cdep, csave = Sbatch.makeCrossSbatch(fields[i], fields[j], xplotkey)
            jobnames.extend(csb)
            dependencies.update(cdep)
            varnames.extend(cvar)
            savefiles.update(csave)

gd.update(savefiles)

if gd["verbose"]:
    print("dependency dictionary: ")
    print(dependencies)

    print("jobnames list: ")
    print(jobnames)

    print("savefiles dictionary:")
    print(savefiles)

    print("varnames list:")
    print(varnames)



print("the global dictionary:")
print(gd)
gdpath = gd['output'] + 'gd.pkl'
w_path = open(gdpath, 'wb')
pkl.dump(gd, w_path, pkl.HIGHEST_PROTOCOL)
w_path.close()

# add hih2 hiptl, tng snapshot, postprocessing files to path,
# creating the pipeline
pipe = open(gd['output']+'sbatch/pipeline.bash', 'w')

pipe.write("#!/bin/bash\n")
pipe.write('GDFILE=%s\n'%gdpath)
# helper method to write jobs and their dependencies
def write_line(varname, sname, jdep=None):
    if jdep is None:
        pipe.write("%s=$(sbatch --export=ALL,GDFILE=$GDFILE %s)\n"%(varname, sname))
    else:
        pipe.write("%s=$(sbatch --export=ALL,GDFILE=$GDFILE --dependency=afterok:"%varname)
        for i in range(len(jdep)):
            if not jdep[i] == jdep[-1]:
                pipe.write('$'+jdep[i]+':')
            else:
                pipe.write('$'+jdep[i])
        pipe.write(" %s)\n"%sname)
    pipe.write("%s=\"${%s##* }\"\n\n"%(varname, varname))
    return

for i in range(len(jobnames)):
    try:
        write_line(varnames[i], jobnames[i], dependencies[varnames[i]])
    except KeyError:
        write_line(varnames[i], jobnames[i])


