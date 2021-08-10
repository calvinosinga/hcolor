
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
    CHUNK = 0 # the groupcat runs don't need to operate on chunks

paths = pickle.load(os.getenv('PATHFILE'),'r')


#####################################
if FIELDNAME == 'hiptl':
   field = hiptl(paths, SIMNAME, SNAPSHOT, AXIS, RESOLUTION, CHUNK, FIELDNAME+'%d'%CHUNK)
else:
   raise NotImplementedError("there is no field named %s"%FIELDNAME)

field.computeGrids()
