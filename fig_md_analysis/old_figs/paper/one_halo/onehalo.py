import hc_lib.plots.figlib as flib
flib.siteFG()
from figrid.figrid import DataList
from figrid.figrid import Figrid
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import copy
import seaborn as sb

box = 'tng100'
snap = [99, 67]
axis = 0
res = 800
files = ['hiptlXgalaxy', 'vnXgalaxy', 'ptlgrid', 'galaxygrid', 'hisubhaloXgalaxy']
master = DataList()
for f in files:
    for s in snap:
        rlib = flib.load(box, s, axis, res, f)
        kmin = rlib.results['pk'][0].xvalues[0]
        BOX = rlib.results['pk'][0].props['box']
        RES = rlib.results['pk'][0].props['grid_resolution']
        master.loadResults(rlib.results['pk'])

rlib = flib.load(box, 99, 0, 800, 'galaxygrid', 'all_gals')
rlib = flib.load(box, 99, 0, 800, 'galaxygrid', 'species')

smfont = 10
larfont = 12
cdict = flib.getCdict()
XBORDER, YBORDER = flib.getBorders()

def matterAuto(ip, name):
    print('MAKING MATTER AUTO POWER SPECTRUM')
    ip['is_auto'] = True
    ip['color'] = ['resolved', 'all']
    ip['gal_species']
    dclist = DataList(master.getMatching(ip))
    fg = Figrid(dclist)
    fg.setRowOrder(['real', 'redshift'])
    fg.arrange('space', '', )
    return