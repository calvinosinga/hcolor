import hc_lib.plots.figlib as flib
flib.siteFG()
from figrid.figrid import DataList
from figrid.figrid import Figrid
import numpy as np
import matplotlib as mpl

box = 'tng100'
snap = [99, 67]
axis = 0
res = 800
files = ['hiptlXgalaxy', 'vnXgalaxy']
master = DataList()
for f in files:
    for s in snap:
        rlib = flib.load(box, s, axis, res, f)
        kmin = rlib.results['pk'][0].xvalues[0]
        master.loadResults(rlib.results['pk'])

smfont = 10
larfont = 12

def color_compare(ip, area_or_middle, smooth, savename):
    def _smooth(ax, data, kwargs):
        shape = int(data[0].shape[0] / 2)
        x = np.zeros(shape)
        ymin = np.zeros_like(x)
        ymax = np.zeros_like(x)

        for i in range(shape):
            x[i] = (data[0][2*i] + data[0][2*i + 1]) / 2
            ymin[i] = (data[1][2*i] + data[1][2*i + 1]) / 2
            ymax[i] = (data[2][2*i] + data[2][2*i + 1]) / 2

        ax.fill_between(x, ymin, ymax, **kwargs)      
        return

    def _middle(ax, data, kwargs):
        y = np.mean(np.array([data[1], data[2]]), axis = 1)
        ax.plot(data[0], y, **kwargs)
        return
    
    def _smoothMiddle(ax, data, kwargs):
        shape = int(data[0].shape[0] / 2)
        x = np.zeros(shape)
        ymin = np.zeros_like(x)
        ymax = np.zeros_like(x)

        for i in range(shape):
            x[i] = (data[0][2*i] + data[0][2*i + 1]) / 2
            ymin[i] = (data[1][2*i] + data[1][2*i + 1]) / 2
            ymax[i] = (data[2][2*i] + data[2][2*i + 1]) / 2
        
        y = np.mean(np.array([ymin, ymax]), axis = 1)
        ax.plot(x, y, **kwargs)
        return
    
    # make ratios
    dl = DataList(master.getMatching(ip))
    rob = flib.makeBlueRedRatio(dl)
    robdl = DataList(rob)
    if area_or_middle == 'middle':
        if smooth:
            robdl.setFunc({'figrid_process':'fill'}, _smoothMiddle)
        else:
            robdl.setFunc({'figrid_process':'fill'}, _middle)
    
    elif smooth:
        robdl.setFunc({'figrid_process':'fill'}, _smooth)
    
    fgrob = Figrid(robdl)
    fgrob.arrange('ratio', 'is_particle', panel_length = 2)
    fkw = {}
    fkw['label'] = 'Real Space'
    fkw['color'] = 'gray'
    fkw['alpha'] = 0.35
    fgrob.makeFills({'space':'real'}, fkw)
    fkw['label'] = 'Redshift Space'
    fkw['color'] = 'tan'
    fgrob.makeFills({'space':'redshift'}, fkw)


    box = dl.getAttrVals('box')[0]
    res = dl.getAttrVals('grid_resolution')[0]
    dl = DataList(master.getMatching(ip))
    fg = Figrid(dl)
    fg.setColOrder(['real', 'redshift'])
    fg.arrange('space', 'is_particle', panel_length = 2, panel_bt = 0.11, yborder = 0.3)
    pargs = {}
    pargs['label'] = 'HI-Blue Cross-Power'
    pargs['color'] = 'blue'
    pargs['alpha'] = 0.55
    fg.makeFills({'color':'blue'}, pargs)
    pargs['label'] = 'HI-Red Cross-Power'
    pargs['color'] = 'red'
    fg.makeFills({'color':'red'}, pargs)
    fg.combineFigrids(fgrob)
    
    fg.plot()

    redslc = (slice(1,fg.dim[0]-1), slice(None))
    realslc = (slice(0, 1), slice(None))
    # fix the axes
    axparams = {}
    flib.setNyq(fg, kmin, res, box)
    axparams['xscale'] = 'log'
    axparams['ylim'] = [0, 2]
    fg.setAxisParams(axparams)
    axparams['yscale'] = 'log'
    axparams['ylim'] = [0.1, 1e4]
    fg.setAxisParams(axparams, slc=redslc)
    axparams['ylim'] = [1, 1e4]
    fg.setAxisParams(axparams, slc = realslc)
    # fix the tick labels
    fg.setDefaultTicksParams()
    fg.setTicks({'labelsize':smfont, 'direction':'in'})
    # labels
    kw = {'fontsize':larfont}
    pknum = fg.dim[0] - 1
    ypos = [0, 1 - 0.5*(fg.panel_length * pknum + fg.panel_bt[1] * (pknum-1)+ fg.yborder[1]) / fg.figsize[1]]
    flib.pklabels(fg, ysub = r'\rm{HI-gal}', ypos = ypos, xtxtkw = kw, ytxtkw = kw)
    txtkw = {}
    txtkw['ha'] = 'center'
    txtkw['va'] = 'top'
    txtkw['fontsize'] = smfont
    fg.setRowLabels(['Real Space', 'Redshift Space', 'Color Ratio'], [0.5, 0.95],
                txtkw)
    fg.makeYLabel(r'P$_{\rm{red}}$ (k) / P$_{\rm{blue}}$ (k)', 
                [0, (0.5 * fg.panel_length + fg.yborder[0]) / fg.figsize[1]], 
                {'va':'center', 'fontsize':larfont})
    lkw = {'frameon':False, 'fontsize':smfont - 1, 'loc':'lower left'}
    fg.drawLegend(lkw, (0,0))
    # lkw['loc'] = 'center right'
    fg.drawLegend(lkw, (2,0))
    fcolors = np.empty(fg.dim, dtype = object)
    trgba = mpl.colors.to_rgba
    alpha = 0.3
    fcolors[:,0] = [trgba('gray', alpha), trgba('tan', alpha), trgba('white')]
    flib.setFacecolor(fg, fcolors)
    flib.plotOnes(fg, (fg.dim[0]-1,0))
    fg.save(savename)
    return box, res

# the red vs blue ratios don't make a lot of sense with the ratios
ip = {'color':['red', 'blue']}
for smoother in [True, False]:
    for plottype in ['middle', 'area']:
        for ss in [99, 67]:
            ip['snapshot'] = ss
            if smoother:
                smoothname = 'smoothed'
            else:
                smoothname = 'nosmooth'
            name = 'redvsblue_noall_%s_%s_%03d.pdf'%(plottype, smoothname, ss)
            box, res = color_compare(ip, plottype, smoother, name)


rbonly = DataList(master.getMatching({'color':['red', 'blue']}))
withrat = flib.makeBlueRedRatio(rbonly)
rbonly.dclist.extend(withrat)

import seaborn as sb
fg = Figrid(rbonly)
fg.setRowOrder(['real', 'redshift'])
fg.setColOrder(['blue', 'red', 'ratio'])
fg.arrange('color', 'space', panel_length = 2, panel_bt = 0.11, yborder = 0.3)
zcols = sb.color_palette('summer', len(master.getAttrVals('snapshot')))
pargs = {}
pargs['label'] = 'z=0'
pargs['color'] = zcols[0]
pargs['alpha'] = 0.55
fg.makeFills({'snapshot': 99}, pargs)
pargs['label'] = 'z=0.5'
pargs['color'] = zcols[1]
fg.makeFills({'snapshot':67}, pargs)
fg.plot()

pkslc = (slice(0,2), slice(None))
# fix the axes
axparams = {}
flib.setNyq(fg, kmin, res, box)
axparams['xscale'] = 'log'
axparams['ylim'] = [0, 2]
fg.setAxisParams(axparams)
axparams['yscale'] = 'log'
axparams['ylim'] = [0.1, 1e4]
fg.setAxisParams(axparams, slc=pkslc)
# axparams['ylim'] = [1, 1e4]
# fg.setAxisParams(axparams, slc=(slice(0,1), slice(0,2)))
# fix the tick labels
fg.setDefaultTicksParams()
fg.setTicks({'labelsize':smfont, 'direction':'in'})
# labels
kw = {'fontsize':larfont}
ypos = [0, 1 - 0.5*(fg.panel_length * 2 + fg.panel_bt[1] * 1 + fg.yborder[1]) / fg.figsize[1]]
flib.pklabels(fg, ysub = r'\rm{HI-gal}', ypos = ypos, xtxtkw = kw, ytxtkw = kw)
txtkw = {}
txtkw['ha'] = 'center'
txtkw['va'] = 'top'
txtkw['fontsize'] = smfont
fg.setRowLabels(['Blue Galaxies', 'Red Galaxies', 'Color Ratio'], [0.5, 0.95],
               txtkw)
txtkw['ha'] = 'left'
txtkw['va'] = 'bottom'
fg.setColLabels(['Real Space', 'Redshift Space'], [0.05, 0.05], txtkw)
fg.makeYLabel(r'P$_{\rm{red}}$ (k) / P$_{\rm{blue}}$ (k)', 
              [0, (0.5 * fg.panel_length + fg.yborder[0]) / fg.figsize[1]], 
              {'va':'center', 'fontsize':larfont})
lkw = {'frameon':False, 'fontsize':smfont - 1, 'loc':'lower left'}
fg.drawLegend(lkw, (1,1))
lkw['loc'] = 'center right'
# fg.drawLegend(lkw, (2,0))
fcolors = np.empty(fg.dim, dtype = object)
trgba = mpl.colors.to_rgba
alpha = 0.15
for i in range(2):
    flib.plotOnes(fg, (2, i))
# fcolors[:,0] = [trgba('blue', alpha), trgba('red', alpha), trgba('white')]
# flib.setFacecolor(fg, fcolors)
fg.save("redvsblue_redshift_evo.pdf")
