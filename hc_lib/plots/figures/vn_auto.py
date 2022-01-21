from hc_lib.plots.fig_lib import FigureLibrary

def fieldnameR_redshiftC_space(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 0.25,
            border = 1):
    """
    This plot is intended to compare how differently the models behave, and replicates the main plot
    intended for the paper between the different HI auto power spectra.
    """
    row_prop = 'fieldname'
    column_prop = 'redshift'
    panel_prop = 'space'
    
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, panel_prop))
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, 'pk')
    linelabels = {'real':'Real Space', 'redshift': 'Redshift Space'}
    linecolors = {'real':'blue', 'redshift':'red'}
    flib = FigureLibrary(figArr)
    # add distortion panels


    flib.createFig(panel_length, panel_bt, border, border)
    flib.plotLines(panel_prop, linelabels, linecolors)
    #flib.addRowLabels(rowlabels)
    flib.addColLabels(collabels)
    flib.logAxis('both')

    flib.removeDefaultTickLabels()
    flib.xLimAdjustToNyquist()
    flib.flushYAxisToData()
    flib.matchAxisLimits(which = 'both')
    flib.defaultAxesLabels()
    flib.addLegend()
    flib.printIprops(iprops)

    # if savefig, then save it, otherwise return it

    if not savePath == '':
        flib.saveFig(savePath, row_prop, column_prop, panel_prop)
        return
    else:
        return flib

def fieldnameR_spaceC_redshift(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 0.25,
            border = 1):
    row_prop = 'fieldname'
    column_prop = 'space'
    panel_prop = 'redshift'
    
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, panel_prop))
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, 'pk')

    linelabels = {}
    pres = figArr[0, 0]
    for i in pres:
        z = i.getProp('redshift')
        linelabels[z] = '%.1f'%z    #print(figArr.shape)
    flib = FigureLibrary(figArr)
    # add distortion panels


    flib.createFig(panel_length, panel_bt, border, border)
    flib.plotLines(panel_prop, linelabels)
    #flib.addRowLabels(rowlabels)
    flib.addColLabels(collabels)
    flib.logAxis('both')

    flib.removeXTickLabels()
    flib.changeTickDirection()
    flib.removeYTickLabels()
    flib.xLimAdjustToNyquist()
    flib.flushYAxisToData()
    flib.matchAxisLimits(which = 'both')
    flib.defaultAxesLabels()
    flib.addLegend()
    flib.printIprops(iprops)

    # if savefig, then save it, otherwise return it

    if not savePath == '':
        flib.saveFig(savePath, row_prop, column_prop, panel_prop)
        return
    else:
        return flib

def fieldnameR_redshiftC_2D(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 0.25,
            border = 1):
    row_prop = 'fieldname'
    column_prop = 'redshift'
    iprops['space'] = 'redshift'
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, '2D'))
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, '2Dpk')

    flib = FigureLibrary(figArr)
    
    flib.createFig(panel_length, panel_bt, border, border, True)
    flib.assignColormaps()
    flib.assign2DNorms()
    flib.addContours()
    flib.plot2D()

    
    flib.changeTickDirection()
    flib.addColLabels(collabels)
    flib.addRowLabels(rowlabels, pos=[0.05, 0.9], color = 'white')
    
    flib.removeDefaultTickLabels()
    flib.defaultAxesLabels(2)
    
    if not savePath == '':
        flib.saveFig(savePath, row_prop, column_prop, '2D')
         
        return None
    else:
        return flib