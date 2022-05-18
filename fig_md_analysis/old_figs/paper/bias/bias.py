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
files = ['hiptlXgalaxy', 'vnXgalaxy', 'galaxygrid', 'hiptlgrid', 'vngrid', 'ptlgrid',
    'hiptlXptl', 'hisubhalogrid', 'hisubhaloXgalaxy', 'hisubhaloXptl', 'vnXptl']
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
PTLSPECIES = ['ptl', 'dm', 'stmass', 'gas']


def addPtlBias():
    for ss in snap:
        for sp in ['real', 'redshift']:
            ptlip = {'fieldname':'ptl', 'ptl_species':'ptl', 'space':sp,
                'snapshot':ss}

            ptl = master.getMatching(ptlip)[0]

            hiip = {'is_hydrogen':True, 'is_particle':True, 'space':sp,
                'snapshot':ss, 'is_auto':True}
            HIs = master.getMatching(hiip)

            galip = {'space':sp, 'snapshot':ss, 'fieldname':'galaxy',
                'gal_species':'stmass', 'gal_res':'deimer'}
            gals = master.getMatching(galip)
            print(len(gals))
            HIbiases = flib.makeObsBias(HIs, ptl)
            galbiases = flib.makeObsBias(gals, ptl)

            master.extend(HIbiases)
            master.extend(galbiases)
            
            
    return

addPtlBias()

def plotPtlBias(ip, savename):
    ip['figlib_process'] = 'obs_bias'
    dl = master.getMatching(ip)
    fg = Figrid(dl)
    rows = ['real', 'redshift']
    cols = [99, 67]
    fg.setRowOrder(rows)
    fg.setColOrder(cols)
    fg.arrange('space', 'snapshot', panel_length = 2, xborder = XBORDER,
        yborder = YBORDER)
    
    fkw = {'label':r'b$_{\rm{HI}}$', 'color':'gray', 'alpha':0.55}
    fg.makeFills({'is_hydrogen':True}, fkw)
    fg.setPlotArgs({'color':'red'}, {'color':cdict['red'], 'label':r'b$_{\rm{Red}}$'})
    fg.setPlotArgs({'color':'blue'}, {'color':cdict['blue'], 'label':r'b$_{\rm{Blue}}$'})
    fg.plot()

    axkw = {}
    axkw['xlim'] = XLIM
    axkw['xscale'] = 'log'
    axkw['ylim'] = [0, 2]
    fg.setAxisParams(axkw)

    fg.setDefaultTicksParams()
    fg.setTicks({'labelsize':smfont, 'direction':'in'})

    fg.makeXLabel('k (cMpc/h)$^{-1}$')
    fg.makeYLabel(r'b$_{\rm{x-m}}$')
    
    tkw = {'fontsize':larfont}
    fg.setRowLabels(['Real Space', 'Redshift Space'], tkw)
    fg.setColLabels(['z=0.0', 'z=0.5'], tkw)

    lkw = {'frameon':False, 'fontsize':smfont - 1, 'loc':'lower left'}
    fg.drawLegend(lkw, (1,1))
    fg.save(savename)
    fg.clf()
    return