
from hicc_library.fields.ptl import ptl
from hicc_library.fields.galaxy import galaxy, galaxy_dust
import sys
import os
import pickle
import h5py as hp
from hicc_library.fields.hiptl import hiptl, hiptl_nH, h2ptl
from hicc_library.fields.hisubhalo import hisubhalo, h2subhalo
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
else:
    outfilepath = gd['grids']+gd[FIELDNAME]%CHUNK

pickle_path = gd['pickles'][FIELDNAME]
outfile = hp.File(outfilepath, 'w')

#####################################
if FIELDNAME == 'hiptlgrid':
    field = hiptl(SIMNAME, SNAPSHOT, AXIS, RESOLUTION, CHUNK, pickle_path,
            gd['verbose'], gd['snapshot'], gd['hih2ptl'])

elif FIELDNAME == 'hiptl_nHgrid':
    field = hiptl_nH(SIMNAME, SNAPSHOT, AXIS, RESOLUTION, CHUNK, pickle_path,
            gd['verbose'], gd['snapshot'], gd['hih2ptl'])
    
elif FIELDNAME == 'hisubhalogrid':
    field = hisubhalo(SIMNAME, SNAPSHOT, AXIS, RESOLUTION, pickle_path, 
            gd['verbose'], gd[SIMNAME], gd['hih2catsh'])

elif FIELDNAME == 'galaxygrid':
    field = galaxy(SIMNAME, SNAPSHOT, AXIS, RESOLUTION, pickle_path, 
            gd['verbose'], gd[SIMNAME])

elif FIELDNAME == 'galaxy_dustgrid':
    field = galaxy_dust(SIMNAME, SNAPSHOT, AXIS, RESOLUTION, pickle_path, 
            gd['verbose'], gd[SIMNAME], gd['dust'])
elif FIELDNAME == 'vngrid':
    field = vn(SIMNAME, SNAPSHOT, AXIS, RESOLUTION, CHUNK, pickle_path,
            gd['verbose'], gd['snapshot'], gd['TREECOOL'])

elif FIELDNAME == 'ptlgrid':
    field = ptl(SIMNAME, SNAPSHOT, AXIS, RESOLUTION, CHUNK, pickle_path,
            gd['verbose'], gd['snapshot'])

elif FIELDNAME == 'h2ptlgrid':
    field = h2ptl(SIMNAME, SNAPSHOT, AXIS, RESOLUTION, CHUNK, pickle_path,
            gd['verbose'], gd['snapshot'], gd['hih2ptl'])

elif FIELDNAME == 'h2subhalo':
    field = h2subhalo(SIMNAME, SNAPSHOT, AXIS, RESOLUTION, pickle_path, 
            gd['verbose'], gd[SIMNAME], gd['hih2catsh'])
else:
    raise NotImplementedError("there is no field named %s"%FIELDNAME)

field.loadHeader(gd['load_header'])
field.computeGrids(outfile)
field.computeAux()
# for fields with chunks, there will already be a pickle file with
# the needed information so we don't need to create a new one with
# each chunk.
if CHUNK == 0 or CHUNK == -1:
    pickle.dump(field, open(pickle_path, 'wb'), pickle.HIGHEST_PROTOCOL)
outfile.close()
