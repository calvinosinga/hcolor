
from hicc_library.fields.galaxy import galaxy, galaxy_dust
import sys
import os
import pickle
from hicc_library.fields.hiptl import hiptl
from hicc_library.fields.hisubhalo import hisubhalo
from hicc_library.fields.vn import vn

FIELDNAME = sys.argv[1]
SIMNAME = sys.argv[2]
SNAPSHOT = int(sys.argv[3])
AXIS = int(sys.argv[4])
RESOLUTION = int(sys.argv[5])
try:
    CHUNK = int(sys.argv[6])
except IndexError:
    CHUNK = -1 # the groupcat runs don't need to operate on chunks


print("the cmd-line arguments for create_grid.py:")
print("fieldname:%s"%FIELDNAME)
print("simulation name:%s"%SIMNAME)
print("snapshot:%d"%SNAPSHOT)
print("axis:%d"%AXIS)
print("resolution:%d"%RESOLUTION)
print("chunk (if not given, will be -1):%d"%CHUNK)

gd = pickle.load(open(os.getenv('GDFILE'),'rb'))
if CHUNK == -1:
    outfilepath = gd['grids']+gd[FIELDNAME]
else:
    outfilepath = gd['grids']+gd[FIELDNAME] %CHUNK
#####################################
if FIELDNAME == 'hiptlgrid':
    field = hiptl(gd, SIMNAME, SNAPSHOT, AXIS, RESOLUTION, CHUNK, outfilepath)
elif FIELDNAME == 'hisubhalogrid':
    field = hisubhalo(gd, SIMNAME, SNAPSHOT, AXIS, RESOLUTION, outfilepath)
elif FIELDNAME == 'galaxygrid':
    field = galaxy(gd, SIMNAME, SNAPSHOT, AXIS, RESOLUTION, outfilepath)
elif FIELDNAME == 'galaxy_dustgrid':
    field = galaxy_dust(gd, SIMNAME, SNAPSHOT, AXIS, RESOLUTION, outfilepath)
elif FIELDNAME == 'vn':
    field = vn(gd, SIMNAME, SNAPSHOT, AXIS, RESOLUTION, CHUNK, outfilepath)
else:
    raise NotImplementedError("there is no field named %s"%FIELDNAME)

field.computeGrids()
field.computeAux()
