from hc_lib.plots.fig_lib import FigureLibrary
    
def redshiftR_spaceC_fieldname(rlib, iprops, rmprops, savePath = '', panel_length = 3, panel_bt = 0.25,
            border = 1):
    """
    Basic plot, shows how the pk of the red and blue galaxies change over time in both redshift
    and real space.
    """
    row_prop = 'redshift'
    column_prop = 'space'
    panel_prop = 'fieldname'
    
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, panel_prop))
    figArr, rowlabels, collabels = rlib.organizeCrossFigure(iprops, row_prop, column_prop, 'pk', 1, rmprops, check = [0,0])   
    linelabels = {'vn':'VN18-Particle', 'hiptl':'hiptl', 'hisubhalo':'hisubhalo'}
    colors = {'vn':'green'}
    flib = FigureLibrary(figArr)

    flib.createFig(panel_length, panel_bt, border, border)
    flib.plotLines(panel_prop, linelabels, colors)
#     # combining the lines
    flib.fillLines('hisubhalo', label='D18-Subhalo', color='orange')
    flib.fillLines('hiptl', label='D18-Particle', color='blue')
    flib.addRowLabels(rowlabels)
    flib.addColLabels(collabels)
    flib.logAxis('both')

    flib.removeDefaultTickLabels()
    flib.changeTickDirection()
    flib.xLimAdjustToNyquist()
    flib.flushYAxisToData()
    flib.matchAxisLimits()
    flib.defaultAxesLabels()
    flib.addLegend()
    flib.printIprops(iprops)

    # if savefig, then save it, otherwise return it

    if not savePath == '':
        flib.saveFig(savePath, row_prop, column_prop, panel_prop)
        return
    else:
        return flib

def redshiftR_fieldnameC_space(rlib, iprops, rmprops, savePath = '', panel_length = 3, panel_bt = 0.25,
            border = 1):
    """
    Basic plot, shows how the pk of the red and blue galaxies change over time in both redshift
    and real space.
    """
    row_prop = 'redshift'
    column_prop = 'fieldname'
    panel_prop = 'space'
    
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, panel_prop))
    figArr, rowlabels, collabels = rlib.organizeCrossFigure(iprops, row_prop, column_prop, 'pk', 1, rmprops, check = [0,0])
    for l in range(len(collabels)):
        if 'vn' in collabels[l]:
            collabels[l] = 'VN18-Particle'
            vnidx = l
        elif 'hiptl' in collabels[l]:
            collabels[l] = 'D18-Particle'
            
        elif 'hisubhalo' in collabels[l]:
            collabels[l] = 'D18-Subhalo'
            
    linelabels = {'real':'Real Space', 'redshift':'Redshift Space'}
    colors = {'real':'blue', 'redshift':'red'}
    flib = FigureLibrary(figArr)
    flib.createFig(panel_length, panel_bt, border, border)
    flib.plotLines(panel_prop, linelabels, colors)
    vn_panels = [(i,vnidx) for i in figArr.shape[0]]
    flib.fillLines('real', label='Real Space', color = 'blue', except_panels=vn_panels)
    flib.fillLines('redshift', label='Redshift Space', color = 'red', except_panels=vn_panels)
    flib.addRowLabels(rowlabels)
    flib.addColLabels(collabels)
    flib.logAxis('both')

    flib.removeDefaultTickLabels()
    flib.changeTickDirection()
    flib.xLimAdjustToNyquist()
    flib.flushYAxisToData()
    flib.matchAxisLimits()
    flib.defaultAxesLabels()
    flib.addLegend()
    flib.printIprops(iprops)

    # if savefig, then save it, otherwise return it

    if not savePath == '':
        flib.saveFig(savePath, row_prop, column_prop, panel_prop)
        return
    else:
        return flib

def fieldnameR_spaceC_redshift(rlib, iprops, rmprops, savePath = '', panel_length = 3, panel_bt = 0.25,
            border = 1):
    """
    Basic plot, shows how the pk of the red and blue galaxies change over time in both redshift
    and real space.
    """
    row_prop = 'fieldname'
    column_prop = 'space'
    panel_prop = 'redshift'
    
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, panel_prop))
    figArr, rowlabels, collabels = rlib.organizeCrossFigure(iprops, row_prop, column_prop, 'pk', 1, rmprops, check = [0,0])   
    flib = FigureLibrary(figArr)
    linelabels = {}
    linecolors = {}
    pres = figArr[0, 0]
    for i in pres:
        z = i.getProp('redshift')
        linelabels[z[0]] = 'z = %.1f'%round(z[0])
    zs = list(linelabels.keys())
    zs = zs.sort()
    color_seq = ['navy', 'blue','cornflowerblue', 'darkturqoise','cyan', 'lightcyan']
    for i in range(len(zs)):
        linecolors[zs[i]] = color_seq[i]

    for l in range(len(rowlabels)):
        if rowlabels[l] == 'vn':
            rowlabels[l] = 'VN18-Particle'
            vnidx = l
        elif rowlabels[l] == 'hiptl':
            rowlabels[l] = 'D18-Particle'
        elif rowlabels[l] == 'hisubhalo':
            rowlabels[l] = 'D18-Subhalo'
    vn_panels = [(vnidx, i) for i in figArr.shape[1]]
    flib.createFig(panel_length, panel_bt, border, border)
    flib.plotLines(panel_prop, linelabels, linecolors)
    for ll in linelabels:
        c = linecolors[ll]
        flib.fillLines(linelabels[ll], ll, color=c,except_panels=vn_panels)
    # combining the lines
    flib.addRowLabels(rowlabels)
    flib.addColLabels(collabels)
    flib.logAxis('both')

    flib.removeDefaultTickLabels()
    flib.changeTickDirection()
    flib.xLimAdjustToNyquist()
    flib.flushYAxisToData()
    flib.matchAxisLimits()
    flib.defaultAxesLabels()
    flib.addLegend()
    flib.printIprops(iprops)

    # if savefig, then save it, otherwise return it

    if not savePath == '':
        flib.saveFig(savePath, row_prop, column_prop, panel_prop)
        return
    else:
        return flib

