from hc_lib.plots.fig_lib import FigureLibrary

def redshiftR_spaceC_color(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 0.25,
            border = 1):
    """
    Basic plot, shows how the pk of the red and blue galaxies change over time in both redshift
    and real space.
    """
    row_prop = 'redshift'
    column_prop = 'space'
    panel_prop = 'color'
    
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, panel_prop))
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, 'pk')
    rowlabels = [r'z=%.1f'%i for i in rowlabels]
    collabels = [i.capitalize() for i in collabels]

    flib = FigureLibrary(figArr)
    # add distortion panels
    dist_panels_idx_list = flib.addRedshiftDistortion((slice(None), 0), 
            (slice(None), 1), panel_prop)
    collabels.append('Distortion')

    flib.createFig(panel_length, panel_bt, border, border)
    flib.plotLines(panel_prop)
    flib.addRowLabels(rowlabels)
    flib.addColLabels(collabels)
    flib.logAxis('y', panel_exceptions = dist_panels_idx_list)
    flib.logAxis('x')

    flib.removeXTickLabels()
    def_ytick_except = flib._defaultTickLabelPanelExceptions('y')
    flib.removeYTickLabels(panel_exceptions = dist_panels_idx_list + def_ytick_except)
    flib.xLimAdjustToNyquist()
    flib.flushYAxisToData()
    flib.matchAxisLimits(which = 'x')
    flib.matchAxisLimits(which = 'y', panel_exceptions = dist_panels_idx_list)
    flib.defaultPKAxesLabels()
    flib.axisLabel('P$_x$(k)/P$_v$(k)', 'y', pos = [1 - border/3/flib.figsize[1], 0.5], rotation = 270)
    flib.addLegend()
    flib.printIprops(iprops)

    # if savefig, then save it, otherwise return it

    if not savePath == '':
        flib.saveFig(savePath, row_prop, column_prop, panel_prop)
        return
    else:
        return flib

def fieldnameR_colorC_species(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 0.25,
            border = 1):
    """
    Visualize the effect of only using stellar mass on the auto pk.
    """
    row_prop = 'fieldname'
    column_prop = 'color'
    panel_prop = 'species'
    
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, panel_prop))
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, 'pk')
    collabels = [i.capitalize() for i in collabels]

    flib = FigureLibrary(figArr)

    flib.createFig(panel_length, panel_bt, border, border)
    flib.plotLines(panel_prop)
    flib.addRowLabels(rowlabels)
    flib.addColLabels(collabels)
    flib.logAxis('both')

    flib.removeDefaultTickLabels()
    flib.xLimAdjustToNyquist()
    flib.flushYAxisToData()
    flib.matchAxisLimits(which = 'both')
    flib.defaultPKAxesLabels()
    flib.addLegend()
    flib.printIprops(iprops)

    # if savefig, then save it, otherwise return it

    if not savePath == '':
        flib.saveFig(savePath, row_prop, column_prop, panel_prop)
        return
    else:
        return flib

def fieldnameR_colorC_mas(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 0.25,
            border = 1):
    """
    Visualize the effect of using CIC or CICW for the mass-assignment scheme.
    """
    row_prop = 'fieldname'
    column_prop = 'color'
    panel_prop = 'mas'
    
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, panel_prop))
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, 'pk')
    collabels = [i.capitalize() for i in collabels]

    flib = FigureLibrary(figArr)

    flib.createFig(panel_length, panel_bt, border, border)
    flib.plotLines(panel_prop)
    flib.addRowLabels(rowlabels)
    flib.addColLabels(collabels)
    flib.logAxis('both')

    flib.removeDefaultTickLabels()
    flib.xLimAdjustToNyquist()
    flib.flushYAxisToData()
    flib.matchAxisLimits(which = 'both')
    flib.defaultPKAxesLabels()
    flib.addLegend()
    flib.printIprops(iprops)

    # if savefig, then save it, otherwise return it

    if not savePath == '':
        flib.saveFig(savePath, row_prop, column_prop, panel_prop)
        return
    else:
        return flib
    

def fieldnameR_colorC_color_cut(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 0.25,
            border = 1):
    """
    Visualize how the color_cut used affects the pk for the color.
    """
    row_prop = 'fieldname'
    column_prop = 'color'
    panel_prop = 'color_cut'
    
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, panel_prop))
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, 'pk')
    collabels = [i.capitalize() for i in collabels]

    flib = FigureLibrary(figArr)

    flib.createFig(panel_length, panel_bt, border, border)
    flib.plotLines(panel_prop)
    flib.addRowLabels(rowlabels)
    flib.addColLabels(collabels)
    flib.logAxis('both')

    flib.removeDefaultTickLabels()
    flib.xLimAdjustToNyquist()
    flib.flushYAxisToData()
    flib.matchAxisLimits(which = 'both')
    flib.defaultPKAxesLabels()
    flib.addLegend()
    flib.printIprops(iprops)

    # if savefig, then save it, otherwise return it

    if not savePath == '':
        flib.saveFig(savePath, row_prop, column_prop, panel_prop)
        return
    else:
        return flib

def redshiftR_colorC_fieldname(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 0.25,
            border = 1):
    """
    Visualize how including prescriptions for dust affects the pk
    """
    row_prop = 'redshift'
    column_prop = 'color'
    panel_prop = 'fieldname'
    
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, panel_prop))
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, 'pk')
    collabels = [i.capitalize() for i in collabels]
    rowlabels = [r'z=%.1f'%i for i in rowlabels]


    flib = FigureLibrary(figArr)

    flib.createFig(panel_length, panel_bt, border, border)
    flib.plotLines(panel_prop)
    flib.addRowLabels(rowlabels)
    flib.addColLabels(collabels)
    flib.logAxis('both')

    flib.removeDefaultTickLabels()
    flib.xLimAdjustToNyquist()
    flib.flushYAxisToData()
    flib.matchAxisLimits(which = 'both')
    flib.defaultPKAxesLabels()
    flib.addLegend()
    flib.printIprops(iprops)

    # if savefig, then save it, otherwise return it

    if not savePath == '':
        flib.saveFig(savePath, row_prop, column_prop, panel_prop)
        return
    else:
        return flib

