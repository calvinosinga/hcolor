
from hicc_library.fields.galaxy import galaxy, galaxy_dust, galaxy_ptl
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
else:
    outfilepath = gd['grids']+gd[FIELDNAME]%CHUNK
outfile = hp.File(outfilepath,'r')
picklepath = outfile['pickle'].attrs['path']
field = pickle.load(open(picklepath, 'rb'))
#####################################


field.computeGrids()
field.computeAux()
