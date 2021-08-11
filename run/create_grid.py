
import sys
import h5py as hp
import os
import pickle
from hicc_library.fields.hiptl import hiptl

FIELDNAME = sys.argv[1]
SIMNAME = sys.argv[2]
SNAPSHOT = int(sys.argv[3])
AXIS = int(sys.argv[4])
RESOLUTION = int(sys.argv[5])
if len(sys.argv) > 4:
    CHUNK = int(sys.argv[5])
else:
    CHUNK = -1 # the groupcat runs don't need to operate on chunks

paths = pickle.load(open(os.getenv('PATHFILE'),'rb'))
if CHUNK == -1:
    outfilepath = paths['grids'] + FIELDNAME + "%sB_%03dS_%dR.hdf5"%(SIMNAME, SNAPSHOT, RESOLUTION)
else:
    outfilepath = paths['grids'] + FIELDNAME + "%sB_%03dS_%dR.%d.hdf5"%(SIMNAME, SNAPSHOT, RESOLUTION,CHUNK)
#####################################
if FIELDNAME == 'hiptl':
    field = hiptl(paths, SIMNAME, SNAPSHOT, AXIS, RESOLUTION, CHUNK, outfilepath)
else:
    raise NotImplementedError("there is no field named %s"%FIELDNAME)

field.computeGrids()
