import sys
import h5py as hp
import numpy as np
from Pk_library import XPk, XXi

GRIDFILE1 = sys.argv[1]
GRIDFILE2 = sys.argv[2]

CROSSLIST = sys.argv[3]

OUTFILE = sys.argv[4]

if len(sys.argv) > 5:
    BOX = sys.argv[5]
else:
    BOX = 75
    AXIS = 0

PATH = '/scratch/zt1/project/diemer-prj/user/cosinga/hcolor/output/'

f1 = hp.File(PATH + GRIDFILE1, 'r')
f2 = hp.File(PATH + GRIDFILE2, 'r')

out = hp.File(OUTFILE, 'w')
xpk_list = np.loadtxt(CROSSLIST, dtype = object)

for i in range(xpk_list.shape[0]):
    grid1 = f1[xpk_list[i][0]][:]
    grid2 = f2[xpk_list[i][1]][:]
    
    name = xpk_list[i][2]

    savelist = xpk_list[i][3:]

    if 'pk' in savelist or '2Dpk' in savelist:

        xpk = XPk([grid1, grid2], BOX, AXIS, MAS = ['CIC', 'CIC'])
    
    if 'xi' in savelist:
        xxi = XXi(grid1, grid2, BOX, MAS = ['CIC', 'CIC'], axis = AXIS)


    for sl in savelist:
        if sl == 'pk':
            data = np.array([xpk.k3D, xpk.XPk[:, 0, 0]])
        elif sl == '2Dpk':
            data = np.array([xpk.kpar, xpk.kper, xpk.PkX2D[:, 0]])
        elif sl == 'xi':
            data = np.array([xxi.r3D, xxi.xi[:, 0]])
        out.create_dataset(name + '_' + sl, data = data)
    
out.close()
    








