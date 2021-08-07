

from run.make_pipeline import RESOLUTION
import sys
from hicc_library.fields.field_super import Field

SIMNAME = sys.argv[1]
SNAPSHOT = int(sys.argv[2])
FIELDNAME = sys.argv[3]
RESOLUTION = int(sys.argv[4])
if len(sys.argv) > 4:
    CHUNK = sys.argv[5]
else:
    CHUNK = 0 # the groupcat runs don't need to operate on chunks


field = Field(FIELDNAME, SIMNAME, SNAPSHOT, RESOLUTION, CHUNK)

field.computeGrids()
field.saveGrids()
