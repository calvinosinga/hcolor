#!/usr/bin/env python3
"""

"""

import sys
import h5py as hp
from hicc_library.results.power import Power
# removing the script name from cmd line arguments

sys.argv.pop(0)
INFILE = sys.argv.pop(0)
OUTFILE = sys.argv.pop(0)
GRIDS = sys.argv # list of grids from which pk is to be computed

pk = Power(INFILE, OUTFILE, GRIDS)

pk.compute()


