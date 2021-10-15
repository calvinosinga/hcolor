import illustris_python as il
import sys
import os
import numpy as np
import h5py as hp
import pickle as pkl

PREFIX = sys.argv.pop(1)
SIMNAME = sys.argv.pop(1)
SNAPSHOT = int(sys.argv.pop(1))
AXIS = int(sys.argv.pop(1))
RESOLUTION = int(sys.argv.pop(1))

sys.argv.pop(0) # removing unneeded script name

RUNNAMES = sys.argv

VERBOSE = int(input("how verbose should the logs be? (0 for limited, 1 for detailed)"))
implemented_fields = ['hiptl', 'hisubhalo', 'galaxy', 'galaxy_dust', 'vn', 'ptl', 'hiptl_nH']
HI_fields = ['hiptl', 'hisubhalo', 'vn', 'hiptl_nH']
matter_fields = ['galaxy','galaxy_dust', 'ptl']

print("output directory prefix:%s"%PREFIX)
print("verbosity:%d"%VERBOSE)
print("simulation name: %s"%SIMNAME)
print("snapshot: %03d"%SNAPSHOT)
print("axis: %d"%AXIS)
print("resolution of grid: %d"%RESOLUTION)
print("runs given: "+str(RUNNAMES))
print("currently implemented fields: "+ str(implemented_fields))

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
gd['pickles'] = {}

yorpfile = open('yorp.bash','w')

# make the create_grids