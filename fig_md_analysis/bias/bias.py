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
files = ['hiptlXgalaxy', 'vnXgalaxy', 'galaxygrid', 'hiptlgrid', 'vngrid', 'ptlgrid']
master = DataList()
for f in files:
    for s in snap:
        rlib = flib.load(box, s, axis, res, f)
        kmin = rlib.results['pk'][0].xvalues[0]
        BOX = rlib.results['pk'][0].props['box']
        RES = rlib.results['pk'][0].props['grid_resolution']
        master.loadResults(rlib.results['pk'])

smfont = 10
larfont = 12
cdict = flib.getCdict()
real_color = cdict['real']
redshift_color = cdict['redshift']
blue_color = cdict['blue']
red_color = cdict['red']
XBORDER, YBORDER = flib.getBorders()
XLIM = flib.getXlim()

def ptlBias(ip, name):
    dl = DataList(master.getMatching(ip))
    ptlip = {'fieldname':'ptl', 'ptl_species':'ptl'}
    ptllist = dl.getMatching(ptlip)
    print(len(ptllist))

    hiip = {'is_hydrogen':True, 'is_particle':True}
    HIlist = dl.getMatching(hiip)
    print(len(HIlist))
    return

for ss in snap:
    ip = {'snapshot':ss}
    name = 'ptl_bias_%03d.png'%ss
    ptlBias(ip, name)