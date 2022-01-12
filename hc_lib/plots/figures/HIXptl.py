from hc_lib.plots.fig_lib import FigureLibrary

def redshiftR_spaceC_fieldname(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 0.25,
            border = 1):
    """
    
    """
    row_prop = 'redshift'
    column_prop = 'space'
    panel_prop = 'fieldname'
    
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, panel_prop))
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, 'pk')
    rowlabels = [r'z=%.1f'%i for i in rowlabels]
    collabels = [i.capitalize() for i in collabels]

    
    flib = FigureLibrary(figArr)
    # add distortion panels
    # dist_panels_idx_list = flib.addRedshiftDistortion((slice(None), 0), 
    #         (slice(None), 1), panel_prop)
    # collabels.append('Distortion')

    flib.createFig(panel_length, panel_bt, border, border)
    flib.plotLines(panel_prop)
    flib.addRowLabels(rowlabels)
    flib.addColLabels(collabels)
    # flib.logAxis('y', panel_exceptions = dist_panels_idx_list)
    # flib.logAxis('x')
    flib.logAxis()

    
    flib.changeTickDirection()
    # flib.removeXTickLabels()
    # def_ytick_except = flib._defaultTickLabelPanelExceptions('y')
    # flib.removeYTickLabels(panel_exceptions = dist_panels_idx_list + def_ytick_except)
    flib.removeDefaultTickLabels()
    flib.xLimAdjustToNyquist()
    flib.flushYAxisToData()
    # flib.matchAxisLimits(which = 'x')
    # flib.matchAxisLimits(which = 'y', panel_exceptions = dist_panels_idx_list)
    flib.matchAxisLimits()
    flib.defaultAxesLabels()
    # flib.axisLabel('P$_\mathrm{x}$(k)/P$_\mathrm{v}$(k)', 'y', pos = [1 - border/3/flib.figsize[1], 0.5], rotation = 270)
    flib.addLegend()
    flib.printIprops(iprops)

    # if savefig, then save it, otherwise return it

    if not savePath == '':
        flib.saveFig(savePath, row_prop, column_prop, panel_prop)
        return
    else:
        return flib