
import sys
import h5py as hp
import os
import pickle
from hicc_library.fields.hiptl import hiptl
from hicc_library.fields.hisubhalo import hisubhalo
from hicc_library.fields.hisubhalo import hisubhalo_num

FIELDNAME = sys.argv[1]
SIMNAME = sys.argv[2]
SNAPSHOT = int(sys.argv[3])
AXIS = int(sys.argv[4])
RESOLUTION = int(sys.argv[5])
if len(sys.argv) > 5:
    CHUNK = int(sys.argv[6])
else:
    CHUNK = -1 # the groupcat runs don't need to operate on chunks

print("the cmd-line arguments for create_grid.py:")
print("fieldname:%s"%FIELDNAME)
print("simulation name:%s"%SIMNAME)
print("snapshot:%d"%SNAPSHOT)
print("axis:%d"%AXIS)
print("resolution:%d"%RESOLUTION)
print("chunk (if not given, will be -1):%d"%CHUNK)

gd = pickle.load(open(os.getenv('PATHFILE'),'rb'))
if CHUNK == -1:
    outfilepath = gd[FIELDNAME]
else:
    outfilepath = gd[FIELDNAME] %CHUNK
#####################################
if FIELDNAME == 'hiptlgrid':
    field = hiptl(gd, SIMNAME, SNAPSHOT, AXIS, RESOLUTION, CHUNK, outfilepath)
elif FIELDNAME == 'hisubhalogrid':
    field = hisubhalo(gd, SIMNAME, SNAPSHOT, AXIS, RESOLUTION, outfilepath)
else:
    raise NotImplementedError("there is no field named %s"%FIELDNAME)

field.computeGrids()
field.computeAux()
