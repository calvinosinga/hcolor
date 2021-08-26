
from hicc_library.fields.ptl import ptl
from hicc_library.fields.galaxy import galaxy, galaxy_dust
import sys
import os
import pickle
import h5py as hp
from hicc_library.fields.hiptl import hiptl
from hicc_library.fields.hisubhalo import hisubhalo
from hicc_library.fields.vn import vn

gd = pickle.load(open(os.getenv('GDFILE'),'rb'))

FIELDNAME = sys.argv[1]
SIMNAME = sys.argv[2]
SNAPSHOT = int(sys.argv[3])
AXIS = int(sys.argv[4])
RESOLUTION = int(sys.argv[5])
try:
    CHUNK = int(sys.argv[6])
except IndexError:
    CHUNK = -1 # the groupcat runs don't need to operate on chunks

if gd['verbose']:
    print("the cmd-line arguments for create_grid.py:")
    print("fieldname:%s"%FIELDNAME)
    print("simulation name:%s"%SIMNAME)
    print("snapshot:%d"%SNAPSHOT)
    print("axis:%d"%AXIS)
    print("resolution:%d"%RESOLUTION)
    print("chunk (if not given, will be -1):%d"%CHUNK)


if CHUNK == -1:
    outfilepath = gd['grids']+gd[FIELDNAME]
    pickle_path = gd['results']+gd[FIELDNAME]+'.pkl'
else:
    outfilepath = gd['grids']+gd[FIELDNAME]%CHUNK
    pickle_path = gd['results']+gd[FIELDNAME]%CHUNK+'.pkl'

outfile = hp.File(outfilepath, 'w')
#####################################
if FIELDNAME == 'hiptlgrid':
    field = hiptl(gd, SIMNAME, SNAPSHOT, AXIS, RESOLUTION, CHUNK, pickle_path,
            gd['verbose'], gd['snapshot'], gd['hih2ptl'])
elif FIELDNAME == 'hisubhalogrid':
    field = hisubhalo(SIMNAME, SNAPSHOT, AXIS, RESOLUTION, pickle_path, 
            gd['verbose'], gd[SIMNAME], gd['hih2catsh'])
    if not gd['hisubhalo_use_cicw']:
        field.useCIC()
elif FIELDNAME == 'galaxygrid':
    field = galaxy(SIMNAME, SNAPSHOT, AXIS, RESOLUTION, pickle_path, 
            gd['verbose'], gd[SIMNAME])
    if not gd['galaxy_use_cicw']:
        field.useCIC()
    if not gd['galaxy_use_stmass']:
        field.useAllMass()
    field.useResolution(gd['galaxy_use_res'])
elif FIELDNAME == 'galaxy_dustgrid':
    field = galaxy_dust(SIMNAME, SNAPSHOT, AXIS, RESOLUTION, pickle_path, 
            gd['verbose'], gd[SIMNAME], gd['dust'])
    if not gd['galaxy_dust_use_cicw']:
        field.useCIC()
    if not gd['galaxy_dust_use_stmass']:
        field.useAllMass()
    field.useResolution(gd['galaxy_dust_use_res'])
elif FIELDNAME == 'vngrid':
    field = vn(SIMNAME, SNAPSHOT, AXIS, RESOLUTION, CHUNK, pickle_path,
            gd['verbose'], gd['snapshot'], gd['TREECOOL'])
elif FIELDNAME == 'ptlgrid':
    field = ptl(SIMNAME, SNAPSHOT, AXIS, RESOLUTION, CHUNK, pickle_path,
            gd['verbose'], gd['snapshot'])
elif FIELDNAME == 'galaxy_ptlgrid':
    field = galaxy_ptl(gd, SIMNAME, SNAPSHOT, AXIS, RESOLUTION, CHUNK, outfilepath)
else:
    raise NotImplementedError("there is no field named %s"%FIELDNAME)

field.loadHeader(gd['load_header'])
field.computeGrids(outfile)
field.computeAux()
pickle.dump(field, open(pickle_path, 'wb'), pickle.HIGHEST_PROTOCOL)
outfile.close()