from hc_lib.plots.fig_lib import FigureLibrary
import numpy as np

def redshiftR_spaceC_species(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 1,
            border = 1):
    
    row_prop = 'redshift'
    column_prop = 'space'
    panel_prop = 'species'
    
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, panel_prop))
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, 'pk')

    linelabels = {'dm': 'Dark Matter', 'gas':'Gas', 'ptl':'All Species', 'stmass':'Stellar'}
    #print(figArr.shape)
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
        flib.saveFig(savePath, row_prop, column_prop, panel_prop)
        return
    else:
        return flib

def redshiftR_speciesC_space(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 1,
            border = 1):
    """
    Basic plot, shows how the pk of the red and blue galaxies change over time in both redshift
    and real space.
    """
    row_prop = 'redshift'
    column_prop = 'species'
    panel_prop = 'space'
    
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, panel_prop))
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, 'pk')

    linelabels = {'real':'Real Space', 'redshift':'Redshift Space'}
    linecolors = {'real':'blue', 'redshift':'red'}
    #print(figArr.shape)
    flib = FigureLibrary(figArr)
    # add distortion panels

    for l in range(len(collabels)):
        if collabels[l] == 'dm':
            collabels[l] = 'Dark Matter'
        elif collabels[l] == 'stmass':
            collabels[l] = 'Stellar Mass'
        elif collabels[l] == 'ptl':
            collabels[l] = 'All Species'
        elif collabels[l] == 'gas':
            collabels[l] = 'Gas'
    
    flib.createFig(panel_length, panel_bt, border, border)
    flib.plotLines(panel_prop, linelabels, linecolors)
    flib.addRowLabels(rowlabels)
    flib.addColLabels(collabels)
    flib.logAxis('both')

    flib.changeTickDirection()
    flib.removeDefaultTickLabels()
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

def speciesR_spaceC_redshift(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 1,
            border = 1):
    """
    More easily visualize the redshift evolution of the power spectrum.
    """
    row_prop = 'color'
    column_prop = 'space'
    panel_prop = 'redshift'
    
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, panel_prop))
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, 'pk')

    for l in range(len(rowlabels)):
        if rowlabels[l] == 'dm':
            rowlabels[l] = 'Dark Matter'
        elif rowlabels[l] == 'stmass':
            rowlabels[l] = 'Stellar Mass'
        elif rowlabels[l] == 'ptl':
            rowlabels[l] = 'All Species'
        elif rowlabels[l] == 'gas':
            rowlabels[l] = 'Gas'
    
    linelabels = {}
    pres = figArr[0, 0]
    for i in pres:
        z = i.getProp('redshift')
        linelabels[z] = '%.1f'%z
    #print(figArr.shape)
    flib = FigureLibrary(figArr)
    # add distortion panels

    flib.createFig(panel_length, panel_bt, border, border)
    flib.plotLines(panel_prop, linelabels)
    flib.addRowLabels(rowlabels)
    flib.addColLabels(collabels)
    flib.logAxis('both')

    flib.changeTickDirection()
    flib.removeDefaultTickLabels()
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

def speciesR_spaceC_slice(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 0.5,
            border = 1):
    
    row_prop = 'species'
    column_prop = 'space'
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, 'slice'))
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, 'slice')
    for l in range(len(rowlabels)):
        if rowlabels[l] == 'dm':
            rowlabels[l] = 'Dark Matter'
        elif rowlabels[l] == 'stmass':
            rowlabels[l] = 'Stellar Mass'
        elif rowlabels[l] == 'ptl':
            rowlabels[l] = 'All Species'
        elif rowlabels[l] == 'gas':
            rowlabels[l] = 'Gas'
    cmap_arr = np.empty_like(figArr, dtype=object)
    cmap_arr[:,:] = 'plasma'
    flib = FigureLibrary(figArr)

    flib.createFig(panel_length, panel_bt, border, border, False)
    flib.plotSlices()

    
    flib.matchColorbarLimits()
    flib.assignColormaps(cmap_arr, under='w')
    flib.makeColorbars('log((M$_*$/M$_\odot$)')

    flib.changeTickDirection()
    flib.addColLabels(collabels)
    flib.addRowLabels(rowlabels)
    flib.removeDefaultTickLabels()
    flib.defaultAxesLabels('slice')
    
    
    if not savePath == '':
        flib.saveFig(savePath, row_prop, column_prop, 'slice')
        return None
    else:
        return flib

def redshiftR_speciesC_2D(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 0.25,
            border = 1):
    """
    Visualize redshift space distortions
    """
    row_prop = 'redshift'
    column_prop = 'species'
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, '2D'))
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, '2Dpk')
    for l in range(len(collabels)):
        if collabels[l] == 'dm':
            collabels[l] = 'Dark Matter'
        elif collabels[l] == 'stmass':
            collabels[l] = 'Stellar Mass'
        elif collabels[l] == 'ptl':
            collabels[l] = 'All Species'
        elif collabels[l] == 'gas':
            collabels[l] = 'Gas'
    cmap_arr = np.empty_like(figArr, dtype=object)
    cmap_arr[:,:] = 'plasma'
    flib = FigureLibrary(figArr)
    
    flib.createFig(panel_length, panel_bt, border, border, True)
    flib.addContours()
    flib.plot2D()
    flib.makeColorbars('P(k$_\parallel$, k$_\perp$) (Mpc/h)$^{-3}$')

    flib.changeTickDirection()
    flib.addColLabels(collabels)
    flib.addRowLabels(rowlabels, is2D=True)
    
    flib.removeDefaultTickLabels()
    flib.defaultAxesLabels(2)
    
    if not savePath == '':
        flib.saveFig(savePath, row_prop, column_prop, '2D')
        return None
    else:
        return flib
    
def axisR_speciesC_2D(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 0.25,
            border = 1):

    row_prop = 'axis'
    column_prop = 'species'
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, '2D'))
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, '2Dpk')
    for l in range(len(collabels)):
        if collabels[l] == 'dm':
            collabels[l] = 'Dark Matter'
        elif collabels[l] == 'stmass':
            collabels[l] = 'Stellar Mass'
        elif collabels[l] == 'ptl':
            collabels[l] = 'All Species'
        elif collabels[l] == 'gas':
            collabels[l] = 'Gas'
    cmap_arr = np.empty_like(figArr, dtype=object)
    cmap_arr[:,:] = 'plasma'
    flib = FigureLibrary(figArr)
    
    flib.createFig(panel_length, panel_bt, border, border, True)
    flib.addContours()
    flib.plot2D()
    flib.makeColorbars('P(k$_\parallel$, k$_\perp$) (Mpc/h)$^{-3}$')

    
    flib.changeTickDirection()
    flib.addColLabels(collabels)
    flib.addRowLabels(rowlabels, is2D=True)
    
    flib.removeDefaultTickLabels()
    flib.defaultAxesLabels(2)
    
    if not savePath == '':
        flib.saveFig(savePath, row_prop, column_prop, '2D')
        return None
    else:
        return flib