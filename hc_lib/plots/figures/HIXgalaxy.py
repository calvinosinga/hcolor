from hc_lib.plots.fig_lib import FigureLibrary

def redshiftR_spaceC_fieldname_distortion(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 1,
            border = 1):
    """
    Basic plot, shows how the pk of the red and blue galaxies change over time in both redshift
    and real space.
    """
    row_prop = 'redshift'
    column_prop = 'space'
    panel_prop = 'fieldname'
    
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, panel_prop))
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, 'pk')
    linelabels = {'vn':'VN18-Particle'}
    colors = {'vn':'green'}

    flib = FigureLibrary(figArr)
    # add distortion panels
    dist_panels_idx_list = flib.addRedshiftDistortion((slice(None), 0), 
            (slice(None), 1), panel_prop)
    collabels.append('Distortion')

    flib.createFig(panel_length, panel_bt, border, border)
    flib.plotLines(panel_prop, linelabels, colors)

    # combining the lines
    flib.fillLines(['hiptl'], label='D18-Particle', color='blue')
    flib.fillLines(['hisubhalo'], label='D18-Subhalo', color='orange')
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
    flib.axisLabel('P$_\mathrm{x}$(k)/P$_\mathrm{v}$(k)', 'y', pos = [1 - border/3/flib.figsize[1], 0.5], rotation = 270)
    flib.addLegend()
    flib.printIprops(iprops)

    # if savefig, then save it, otherwise return it

    if not savePath == '':
        flib.saveFig(savePath, row_prop, column_prop, panel_prop, 
                'distortion_panel')
        return
    else:
        return flib

    
def redshiftR_spaceC_fieldname_no_distortion(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 1,
            border = 1):
    """
    Basic plot, shows how the pk of the red and blue galaxies change over time in both redshift
    and real space.
    """
    row_prop = 'redshift'
    column_prop = 'space'
    panel_prop = 'fieldname'
    
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, panel_prop))
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, 'pk')
    #linelabels = {'[\'vn\', \'galaxy\']':'VN18-Particle'}
    #colors = {'[\'vn\', \'galaxy\']':'green'}

    flib = FigureLibrary(figArr)

    flib.createFig(panel_length, panel_bt, border, border)
    flib.plotLines(panel_prop)

    # combining the lines
    flib.fillLines(['[\'hisubhalo\', \'galaxy\']'], label='D18-Subhalo X All Galaxies', color='orange')
    flib.fillLines(['[\'hiptl\', \'galaxy\']'], label='D18-Particle X All Galaxies', color='blue')
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
        flib.saveFig(savePath, row_prop, column_prop, panel_prop, 
                'no_distortion')
        return
    else:
        return flib

def redshiftR_fieldnameC_space(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 1,
            border = 1):
    """
    """
    row_prop = 'redshift'
    column_prop = 'fieldname'
    panel_prop = 'space'
    
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, panel_prop))
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, 'pk')
    linelabels = {'real':'Real Space', 'redshift':'Redshift Space'}
    colors = {'real': 'blue', 'redshift':'red'}

    flib = FigureLibrary(figArr)

    flib.createFig(panel_length, panel_bt, border, border)
    flib.plotLines(panel_prop, linelabels, colors)

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

def fieldnameR_spaceC_redshift(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 1,
            border = 1):
    """
    Basic plot, shows how the pk of the red and blue galaxies change over time in both redshift
    and real space.
    """
    row_prop = 'fieldname'
    column_prop = 'space'
    panel_prop = 'redshift'
    
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, panel_prop))
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, 'pk')

    linelabels = {}
    pres = figArr[0, 0]
    for i in pres:
        z = i.getProp('redshift')
        linelabels[z] = '%.1f'%z

    flib = FigureLibrary(figArr)
    # add distortion panels
    dist_panels_idx_list = flib.addRedshiftDistortion((slice(None), 0), 
            (slice(None), 1), panel_prop)
    collabels.append('Distortion')

    flib.createFig(panel_length, panel_bt, border, border)
    flib.plotLines(panel_prop, linelabels)

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
    flib.axisLabel('P$_\mathrm{x}$(k)/P$_\mathrm{v}$(k)', 'y', pos = [1 - border/3/flib.figsize[1], 0.5], rotation = 270)
    flib.addLegend()
    flib.printIprops(iprops)

    # if savefig, then save it, otherwise return it

    if not savePath == '':
        flib.saveFig(savePath, row_prop, column_prop, panel_prop, 
                'distortion_panel')
        return
    else:
        return flib
