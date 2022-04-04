import hc_lib.plots.figlib as flib
flib.siteFG()
from figrid.figrid import DataList
from figrid.figrid import Figrid
import numpy as np
import seaborn as sb
import matplotlib as mpl
import copy

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
BOX = rlib.results['pk'][0].props['box']
RES = rlib.results['pk'][0].props['grid_resolution']
cdict = flib.getCdict()
XBORDER = [0.75, 0.1]
def space_compare(ip, name):
    print('COMPARING SPACES')
    withall = 'resolved' in ip['color']
    dl = DataList(copy.deepcopy(master.getMatching(ip)))
    rsd = flib.makeRSD(dl)
    rsddl = DataList(rsd)
    fgrsd = Figrid(rsddl)
    fgrsd.arrange('ratio', '', panel_length = 2)
    fkw = {}
    fkw['label'] = 'HI-Blue Galaxy\nCross-Power'
    fkw['color'] = cdict['blue']
    fkw['alpha'] = 0.55
    fgrsd.makeFills({'color':'blue'}, fkw)
    fkw['label'] = 'HI-Red Galaxy\nCross-Power'
    fkw['color'] = cdict['red']
    fgrsd.makeFills({'color':'red'}, fkw)
    if withall:
        fkw['label'] = 'HI-Galaxy\nCross-Power'
        fkw['color'] = cdict['resolved']
        fgrsd.makeFills({'color':'resolved'}, fkw)

    dl = DataList(copy.deepcopy(master.getMatching(ip)))
    fg = Figrid(dl)
    if withall:
        fg.setColOrder(['blue', 'red', 'resolved'])
    else:
        fg.setColOrder(['blue', 'red'])
    fg.arrange('color', '', panel_length = 2, xborder = XBORDER, yborder = [0.5, 0.1])
    fg.combineFigrids(fgrsd)
    pargs = {}
    pargs['label'] = 'Redshift Space'
    pargs['color'] = cdict['real']
    pargs['alpha'] = 0.55
    fg.makeFills({'space':'real'}, pargs)
    pargs['label'] = 'Real Space'
    pargs['color'] = cdict['redshift']
    fg.makeFills({'space':'redshift'}, pargs)
    fg.plot()
    pkslc = (slice(0,fg.dim[0]-1), slice(None))
    # fix the axes
    axparams = {}
    # flib.setNyq(fg, kmin, RES, BOX)
    axparams['xscale'] = 'log'
    axparams['ylim'] = [0, 1.75]
    axparams['xlim'] = [kmin, 20]
    fg.setAxisParams(axparams)
    axparams['yscale'] = 'log'
    axparams['ylim'] = [0.1, 1e4]
    fg.setAxisParams(axparams, slc=pkslc)
    fg.setDefaultTicksParams()
    fg.setTicks({'labelsize':smfont, 'direction':'in'})
    kw = {'fontsize':larfont}
    ypos = [fg.xborder[0] * 0.1 / fg.figsize[0], 1 - 0.5*(np.sum(fg.panel_heights[:-1]) + fg.panel_bt[1] * (fg.dim[1] - 2) + fg.yborder[1]) / fg.figsize[1]]
    flib.pklabels(fg, ysub = r'\rm{HI-gal}', ypos = ypos, xtxtkw = kw, ytxtkw = kw)
    txtkw = {}
    txtkw['ha'] = 'center'
    txtkw['va'] = 'top'
    txtkw['fontsize'] = smfont
    if withall:
        fg.setRowLabels(['Blue Galaxies', 'Red Galaxies', 'All Galaxies', 'Redshift Space\nDistortions'], [0.5, 0.95],
                    txtkw)
    else:
        fg.setRowLabels(['Blue Galaxies', 'Red Galaxies', 'Redshift Space\nDistortions'], [0.5, 0.95],
            txtkw)
    
    fg.makeYLabel(r'P$_{\rm{s}}$ (k) / P$_{\rm{r}}$ (k)', 
                [ypos[0], (0.5 * fg.panel_heights[-1] + fg.yborder[0]) / fg.figsize[1]], 
                {'va':'center', 'fontsize':larfont})
    lkw = {'frameon':False, 'fontsize':smfont - 1, 'loc':'lower left'}
    fg.drawLegend(lkw, (0,0))
    lkw['loc'] = 'center right'
    
    #fg.drawLegend(lkw, (fg.dim[0]-1,0))

    fcolors = np.empty(fg.dim, dtype = object)
    trgba = mpl.colors.to_rgba
    alpha = 0.15
    if withall:
        fcolors[:,0] = [trgba(cdict['blue'], alpha), trgba(cdict['red'], alpha), trgba(cdict['resolved'], alpha), trgba('white', alpha)]
    else:
        fcolors[:,0] = [trgba(cdict['blue'], alpha), trgba(cdict['red'], alpha), trgba('white', alpha)]
    flib.setFacecolor(fg, fcolors)
    flib.plotOnes(fg, (fg.dim[0]-1,0))
    fg.save(name)
    return

withall = ['red', 'blue', 'resolved']
noall = ['red', 'blue']

for a in [withall, noall]:


    for ss in [99, 67]:

        isall = a is withall
        if isall:
            allstr = 'withall'
        else:
            allstr = 'noall'

        name = 'space_%s_%03d.png'%(allstr, ss)

        ip = {}
        ip['snapshot'] = ss
        ip['color'] = a
        
        space_compare(ip, name)

space_compare({'snapshot':99, 'color':noall}, 'space_comparison_FINAL.pdf')
def zevo_space(ip, savename):
    withall = 'resolved' in ip['color']
    dc_list = DataList(copy.deepcopy(master.getMatching(ip)))
    rsd = flib.makeRSD(dc_list)
    dc_list.dclist.extend(rsd)
    fg = Figrid(dc_list)
    fg.setRowOrder(['real', 'redshift', 'rsd'])
    if withall:
        colorder = ['blue', 'red', 'resolved']
    else:
        colorder = ['blue', 'red']
    fg.setColOrder(colorder)
    fg.arrange('space', 'color', panel_length = 2, xborder = XBORDER, yborder = [0.5, 0.1])
    
    fkw = {}
    fkw['alpha'] = 0.55
    zcols = cdict['zevo']
    for cv in fg.colValues:
        if cv in zcols:
            fkw['label'] = 'z=0.0'
            fkw['color'] = zcols[cv][0]
            fg.makeFills({'snapshot':99, 'color':cv}, fkw)
            fkw['label'] = 'z=0.5'
            fkw['color'] = zcols[cv][1]
            fg.makeFills({'snapshot':67, 'color':cv}, fkw)


    fg.plot()

    realslc = (slice(0,1), slice(None))
    redshiftslc = (slice(1,2), slice(None))
    # fix the axes
    axparams = {}
    # flib.setNyq(fg, kmin, RES, BOX)
    axparams['xscale'] = 'log'
    axparams['ylim'] = [0, 1.5]
    axparams['xlim'] = [kmin, 20]
    fg.setAxisParams(axparams)
    axparams['yscale'] = 'log'
    axparams['ylim'] = [0.1, 1e4]
    fg.setAxisParams(axparams, slc=redshiftslc)
    axparams['ylim'] = [1, 1e4]
    fg.setAxisParams(axparams, slc=realslc)
    # fix the tick labels
    fg.setDefaultTicksParams()
    fg.setTicks({'labelsize':smfont, 'direction':'in'})
    # labels
    kw = {'fontsize':larfont}
    ypos = [fg.xborder[0] * 0.1 / fg.figsize[0], 1 - 0.5*(np.sum(fg.panel_heights[:-1]) + fg.panel_bt[1] * (fg.dim[1] - 2) + fg.yborder[1]) / fg.figsize[1]]
    flib.pklabels(fg, ysub = r'\rm{HI-gal}', ypos = ypos, xtxtkw = kw, ytxtkw = kw)
    txtkw = {}
    txtkw['ha'] = 'center'
    txtkw['va'] = 'top'
    txtkw['fontsize'] = smfont
    fg.setRowLabels(['Real Space', 'Redshift Space', 'Redshift Space\nDistortions'], [0.5, 0.95],
                txtkw)
    txtkw['ha'] = 'left'
    txtkw['va'] = 'bottom'
    if withall:
        collabels = ['Blue Galaxies', 'Red Galaxies', 'All Galaxies']
    else:
        collabels = ['Blue Galaxies', 'Red Galaxies']
    fg.setColLabels(collabels, [0.05, 0.05], txtkw)
    fg.makeYLabel(r'P$_{\rm{s}}$ (k) / P$_{\rm{r}}$ (k)', 
                [ypos[0], (0.5 * fg.panel_heights[-1] + fg.yborder[0]) / fg.figsize[1]], 
                {'va':'center', 'fontsize':larfont})
    lkw = {'frameon':False, 'fontsize':smfont - 1, 'loc':'lower left'}
    fg.drawLegend(lkw, (1,1))
    lkw['loc'] = 'center right'
    # fg.drawLegend(lkw, (2,0))
    # fcolors = np.empty(fg.dim, dtype = object)
    # trgba = mpl.colors.to_rgba
    # alpha = 0.15
    for i in range(fg.dim[1]):
        flib.plotOnes(fg, (2, i))
    # fcolors[:,0] = [trgba('blue', alpha), trgba('red', alpha), trgba('white')]
    # flib.setFacecolor(fg, fcolors)
    fg.save(savename)
    return


for a in [withall, noall]:
    isall = a is withall
    if isall:
        allstr = 'withall'
    else:
        allstr = 'noall'

    name = 'space_zevo_%s.png'%(allstr)

    ip = {}
    ip['color'] = a
    
    zevo_space(ip, name)
zevo_space({'color':noall}, 'space_zevo_FINAL.pdf') 
