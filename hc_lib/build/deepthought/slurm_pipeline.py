import os
from sbatch import Sbatch
import pickle as pkl
from hc_lib.build.gd import IODict
from hc_lib.build.input import Input
from hc_lib.build.deepthought.sbatch import Sbatch

OUT_PATH = '/home/cosinga/scratch/hcolor/output/'
TNG_PATH = ''
#HIH2 = '/lustre/cosinga/tng100/'
HCOLOR = '/home/cosinga/scratch/hcolor/'

tng_dict = {
    'tng100':'/home/cosinga/scratch/L75n1820TNG', 
    'tng300':'/lustre/kleidig/illustris/L205n2500TNG',
    'tng100-2':'/home/cosinga/scratch/L75n910TNG', 
    'tng100-3':'/home/cosinga/scratch/L75n455TNG', 
    'tng50':'L35n2160TNG'
    }
ioobj = Input()
rp = ioobj.getParams()
runs = ioobj.getRuns()
TNG_PATH += tng_dict[rp['sim']] + '/'
gdobj = IODict(rp, runs, OUT_PATH, TNG_PATH, HCOLOR)
#the hih2 particles are in Benedikt's lustre directory
#gdobj.add('hih2ptl', HIH2 + "hih2_particles_%03d"%rp['snap'] + ".%d.hdf5")
gd = gdobj.getGlobalDict()
pd = gdobj.getPathDict()

fields = []
for i in runs:
    pd.update(gd)
    fields.append(Sbatch(pd, i, rp))

dependencies = {}
jobnames = []
varnames = []
savefiles = {}

# make creating grids, combining grids, auto sbatch
for f in range(len(fields)):
    if ioobj.isCat(runs[f]):
        fields[f].isCat()
    
    svars, sjobs, sdeps, ssave = fields[f].makeSbatch()
    jobnames.extend(sjobs)
    dependencies.update(sdeps)
    varnames.extend(svars)
    savefiles.update(ssave)
    key = fields[f].fieldname+'grid'
    
    gd['pickles'][key] = pd['results'] + fields[f]._get_base_name(key) + '.pkl'

# make cross sbatch
for i in range(len(fields)):
    for j in range(len(fields)):
        fn1 = fields[i].fieldname
        fn2 = fields[j].fieldname
        galXgal = (fn1 == 'galaxy' and fn2 == 'galaxy')
        galXptl = (fn1 == 'galaxy' and fn2 == 'ptl')
        if (ioobj.isHyd(fn1) and ioobj.isMat(fn2)) or galXgal or galXptl:
            cvar, csb, cdep, csave = Sbatch.makeCrossSbatch(fields[i], fields[j])
            jobnames.extend(csb)
            dependencies.update(cdep)
            varnames.extend(cvar)
            savefiles.update(csave)
            rtup = (rp['sim'], rp['snap'], rp['axis'], rp['res'])
            gd['pickles'][fn1 + 'X' + fn2] = pd['results'] + fn1 + 'X' + fn2 + \
                    "_%sB_%03dS_%dA_%dR.pkl"%rtup

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

gdpath = pd['output'] + 'gd.pkl'
w_path = open(gdpath, 'wb')
pkl.dump(gd, w_path, pkl.HIGHEST_PROTOCOL)
w_path.close()

# creating the pipeline
pipe = open(pd['output']+'sbatch/pipeline.bash', 'w')

pipe.write("#!/bin/bash\n")
pipe.write('GDFILE=%s\n'%gdpath)
# helper method to write jobs and their dependencies
def write_line(varname, sname, jdep=None):
    if jdep is None:
        pipe.write("%s=$(sbatch --export=ALL,GDFILE=$GDFILE %s)\n"%(varname, sname))
    else:
        pipe.write("%s=$(sbatch --export=ALL,GDFILE=$GDFILE --dependency=afterok:"%varname)
        written_deps = []
        dep_str = ''
        for i in range(len(jdep)):
            
            if not jdep[i] in written_deps:
                dep_str+='$'+jdep[i]+':'
                written_deps.append(jdep[i])
        
        if dep_str[-1] == ':':
            dep_str = dep_str[:-1]
        
        pipe.write(dep_str)
        pipe.write(" %s)\n"%sname)
    pipe.write("%s=\"${%s##* }\"\n\n"%(varname, varname))
    return

for i in range(len(jobnames)):
    try:
        write_line(varnames[i], jobnames[i], dependencies[varnames[i]])
    except KeyError:
        write_line(varnames[i], jobnames[i])
