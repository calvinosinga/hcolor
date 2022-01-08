from hc_lib.plots.fig_lib import FigureLibrary

def redshiftR_spaceC_model(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 0.25,
            border = 1):
    """
    This plot is intended to compare how differently the models behave, and replicates the main plot
    intended for the paper between the different HI auto power spectra.
    """
    row_prop = 'redshift'
    column_prop = 'space'
    panel_prop = 'model'
    
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

def modelR_spaceC_map(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 0.25,
            border = 1):
    """
    Makes it easier to visualize if there is any scale-dependence in the variance between mass and temp
    maps within redshift and real space.
    """
    row_prop = 'model'
    column_prop = 'space'
    panel_prop = 'map'
    
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, panel_prop))

    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, 'pk')
    rowlabels = [i.replace('_', '') for i in rowlabels]
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

def redshiftR_mapC_model(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 0.25,
            border = 1):
    """
    Visualizes how the variance between the temperature and mass maps changes depending on model.
    """
    row_prop = 'redshift'
    column_prop = 'map'
    panel_prop = 'model'

    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, 'pk')
    collabels = [i.capitalize() for i in collabels]
    rowlabels = [r'z=%.1f'%i for i in rowlabels]

    flib = FigureLibrary(figArr)
    flib.createFig(panel_length, panel_bt, border, border)

    flib.plotLines(panel_prop)
    flib.addRowLabels(rowlabels)
    flib.addColLabels(collabels)
    flib.logAxis()
    flib.removeDefaultTickLabels()
    flib.xLimAdjustToNyquist()
    flib.flushYAxisToData()
    flib.matchAxisLimits()
    flib.defaultPKAxesLabels()
    flib.addLegend()
    flib.printIprops(iprops)

    # if savefig, then save it, otherwise return it

    if not savePath == '':
        flib.saveFig(savePath, row_prop, column_prop, panel_prop)
        return
    else:
        return flib
    
def redshiftR_modelC_space(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 0.25,
            border = 1):
    """
    Useful for easier comparison of a single model between redshift and real space.
    """
    row_prop = 'redshift'
    column_prop = 'model'
    panel_prop = 'space'

    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, 'pk')

    flib = FigureLibrary(figArr)
    flib.createFig(panel_length, panel_bt, border, border)

    flib.plotLines(panel_prop)
    flib.addRowLabels(rowlabels)
    flib.addColLabels(collabels)
    flib.logAxis()
    flib.removeDefaultTickLabels()
    flib.xLimAdjustToNyquist()
    flib.flushYAxisToData()
    flib.matchAxisLimits()
    flib.defaultPKAxesLabels()
    flib.addLegend()
    flib.printIprops(iprops)

    # if savefig, then save it, otherwise return it

    if not savePath == '':
        flib.saveFig(savePath, row_prop, column_prop, panel_prop)
        return
    else:
        return flib
    

def modelR_spaceC_box(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 0.25,
            border = 1):

    row_prop = 'model'
    column_prop = 'space'
    panel_prop = 'box'
    
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, panel_prop))
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, 'pk')
    rowlabels = [i.replace('_', '') for i in rowlabels]

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
    

def modelR_spaceC_gridResolution(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 0.25,
            border = 1):
    row_prop = 'model'
    column_prop = 'space'
    panel_prop = 'grid_resolution'
    
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, panel_prop))
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, 'pk')
    rowlabels = [i.replace('_', '') for i in rowlabels]
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
    

def modelR_spaceC_simResolution(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 0.25,
            border = 1):
    row_prop = 'model'
    column_prop = 'space'
    panel_prop = 'sim_resolution'
    
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, panel_prop))
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, 'pk')
    rowlabels = [i.replace('_', '') for i in rowlabels]

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
    

def redshiftR_spaceC_axis(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 0.25,
            border = 1):
    row_prop = 'redshift'
    column_prop = 'space'
    panel_prop = 'axis'
    
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
    return
