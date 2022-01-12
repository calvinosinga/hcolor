from hc_lib.plots.fig_lib import FigureLibrary

def redshiftR_spaceC_color(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 1,
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
    linelabels = {'blue' : 'Blue Galaxies', 'red' : 'Red Galaxies'}
    colors = {'blue':'blue', 'red':'red'}
    #print(figArr.shape)
    flib = FigureLibrary(figArr)
    # add distortion panels
    dist_panels_idx_list = flib.addRedshiftDistortion((slice(None), 0), 
            (slice(None), 1), panel_prop)
    collabels.append('Distortion')

    flib.createFig(panel_length, panel_bt, border, border)
    flib.plotLines(panel_prop, labels=linelabels, colors=colors)
    flib.addRowLabels(rowlabels)
    flib.addColLabels(collabels)
    flib.logAxis('y', panel_exceptions = dist_panels_idx_list)
    flib.logAxis('x')

    flib.removeXTickLabels()
    flib.changeTickDirection()
    def_ytick_except = flib._defaultTickLabelPanelExceptions('y')
    flib.removeYTickLabels(panel_exceptions = dist_panels_idx_list + def_ytick_except)
    flib.xLimAdjustToNyquist()
    flib.flushYAxisToData()
    flib.matchAxisLimits(which = 'x')
    flib.matchAxisLimits(which = 'y', panel_exceptions = dist_panels_idx_list)
    flib.defaultAxesLabels()
    flib.axisLabel('P$_\mathrm{x}$(k)/P$_\mathrm{v}$(k)', 'y', pos = [1 - border/3/flib.figsize[1], 0.5], rotation = 270, usetex=True)
    flib.addLegend()
    flib.printIprops(iprops)

    # if savefig, then save it, otherwise return it

    if not savePath == '':
        flib.saveFig(savePath, row_prop, column_prop, panel_prop)
        return
    else:
        return flib

def spaceR_colorC_species(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 0.25,
            border = 1):
    """
    Visualize the effect of only using stellar mass on the auto pk.
    """
    row_prop = 'space'
    column_prop = 'color'
    panel_prop = 'species'
    
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, panel_prop))
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, 'pk')
    collabels = [i.capitalize() for i in collabels]
    rowlabels = [i.capitalize() for i in rowlabels]
    linelabels = {'stmass':'Stellar Particles', 'total':'All Particles'}

    flib = FigureLibrary(figArr)

    flib.createFig(panel_length, panel_bt, border, border)
    flib.plotLines(panel_prop, linelabels)
    flib.addRowLabels(rowlabels)
    flib.addColLabels(collabels)
    flib.logAxis('both')

    flib.removeDefaultTickLabels()
    flib.xLimAdjustToNyquist()
    flib.flushYAxisToData()
    flib.changeTickDirection()
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

def spaceR_colorC_mas(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 0.25,
            border = 1):
    """
    Visualize the effect of using CIC or CICW for the mass-assignment scheme.
    """
    row_prop = 'space'
    column_prop = 'color'
    panel_prop = 'mas'
    
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, panel_prop))
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, 'pk')
    collabels = [i.capitalize() for i in collabels]
    rowlabels = [i.capitalize() for i in rowlabels]
    flib = FigureLibrary(figArr)

    flib.createFig(panel_length, panel_bt, border, border)
    flib.plotLines(panel_prop)
    flib.addRowLabels(rowlabels)
    flib.addColLabels(collabels)
    flib.logAxis('both')

    flib.changeTickDirection()
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
    for r in range(len(rowlabels)):
        if rowlabels[r] == 'galaxy':
            rowlabels[r] = 'Fiducial'
        if rowlabels[r] == 'galaxy_dust':
            rowlabels[r] = 'Dust Model'

    collabels = [i.capitalize() for i in collabels]
    colcuts = rlib.getVals('pk', 'color_cut')
    linelabels = {}
    linests = {}
    for c in colcuts:
        if '0' == c[0]:
            linelabels[c] = 'g-r = %s'%c
            if '0.50' == c or '0.70' == c:
                linests[c] = ':'
            else:
                linests[c] = '-'
        else:
            linests[c] = '--'

    linelabels['visual_inspection'] = 'D18'
    flib = FigureLibrary(figArr[:,:-1]) # removing resolved column

    flib.createFig(panel_length, panel_bt, border, border)
    flib.plotLines(panel_prop, linelabels, linestyles=linests)
    flib.addRowLabels(rowlabels[:-1])
    flib.addColLabels(collabels[:-1])
    flib.logAxis('both')

    flib.changeTickDirection()
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
    linelabels = {'galaxy_dust':'Dust Model', 'galaxy':'Fiducial'}
    linestyles = {'galaxy_dust':'--', 'galaxy':'-'}
    flib = FigureLibrary(figArr)
    

    flib.createFig(panel_length, panel_bt, border, border)
    flib.plotLines(panel_prop, linelabels, linestyles=linestyles)
    flib.addRowLabels(rowlabels)
    flib.addColLabels(collabels)
    flib.logAxis('both')

    flib.removeDefaultTickLabels()
    flib.xLimAdjustToNyquist()
    flib.flushYAxisToData()
    flib.changeTickDirection()
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

def axisR_colorC_fieldname(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 0.25,
            border = 1):
    """
    Visualize if the line of sight affects the dust vs no dust comparison.
    """
    row_prop = 'axis'
    column_prop = 'color'
    panel_prop = 'fieldname'
    
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, panel_prop))
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, 'pk')
    collabels = [i.capitalize() for i in collabels]
    rowlabels = [r'axis=%d'%i for i in rowlabels]
    linelabels = {'galaxy_dust':'Dust Model', 'galaxy':'Fiducial'}
    linestyles = {'galaxy_dust':'--', 'galaxy':'-'}
    flib = FigureLibrary(figArr)
    

    flib.createFig(panel_length, panel_bt, border, border)
    flib.plotLines(panel_prop, linelabels, linestyles=linestyles)
    flib.addRowLabels(rowlabels)
    flib.addColLabels(collabels)
    flib.logAxis('both')

    flib.removeDefaultTickLabels()
    flib.xLimAdjustToNyquist()
    flib.flushYAxisToData()
    flib.changeTickDirection()
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
        
def color_cutR_colorC_gal_res(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 0.25,
            border = 1):
    """
    Visualize how the color_cut used affects the pk for the color.
    """
    row_prop = 'color_cut'
    column_prop = 'color'
    panel_prop = 'gal_res'
    
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
    flib.defaultAxesLabels()
    flib.addLegend()
    flib.printIprops(iprops)

    # if savefig, then save it, otherwise return it

    if not savePath == '':
        flib.saveFig(savePath, row_prop, column_prop, panel_prop)
        return
    else:
        return flib

def make_histograms(rlib, savePath=''):
    print(rlib.hists)
    return