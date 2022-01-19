from hc_lib.plots.fig_lib import FigureLibrary
import numpy as np

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
    linelabels = {'vn':'VN18-Particle'}
    colors = {'vn':'green'}

    flib = FigureLibrary(figArr)

    flib.createFig(panel_length, panel_bt, border, border)
    flib.plotLines(panel_prop, linelabels, colors)

    # combining the lines
    flib.fillLines(['hiptl'], label='D18-Particle', color='blue')
    flib.fillLines(['hisubhalo'], label='D18-Subhalo', color='orange')
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


def fieldnameR_spaceC_slice(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 1,
            border = 1):
    row_prop = 'fieldname'
    column_prop = 'space'
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, 'slice'))
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, 'slice')
    for l in range(len(rowlabels)):
        if rowlabels[l] == 'vn':
            rowlabels[l] = 'VN18-Particle'
        elif rowlabels[l] == 'ptl':
            rowlabels[l] = 'Gas'
        elif rowlabels[l] == 'hiptl':
            rowlabels[l] = 'D18-Particle'
        elif rowlabels[l] == 'hisubhalo':
            rowlabels[l] = 'D18-Subhalo'
    cmap_arr = np.empty_like(figArr, dtype=object)
    cmap_arr[:,:] = 'plasma'
    flib = FigureLibrary(figArr)

    flib.createFig(panel_length, panel_bt, border, border, False)
    flib.plotSlices()

    
    flib.matchColorbarLimits()
    flib.assignColormaps(cmap_arr, under='w')
    flib.makeColorbars('log M$_*$/M$_\odot$')

    flib.changeTickDirection()
    flib.addColLabels(collabels)
    flib.addRowLabels(rowlabels, is2D=True)
    flib.removeDefaultTickLabels()
    flib.defaultAxesLabels('slice')
    
    
    if not savePath == '':
        flib.saveFig(savePath, row_prop, column_prop, 'slice')
        return None
    else:
        return flib

def fieldnameR_redshiftC_axis(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 1,
            border = 1):
    row_prop = 'fieldname'
    column_prop = 'redshift'
    panel_prop = 'axis'
    
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, panel_prop))
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, 'pk')

    linelabels = {0 : 'X-axis', 1 : 'Y-axis', 2:'Z-axis'}

    for l in range(len(rowlabels)):
        if rowlabels[l] == 'vn':
            rowlabels[l] = 'VN18-Particle'
        elif rowlabels[l] == 'ptl':
            rowlabels[l] = 'Gas'
        elif rowlabels[l] == 'hiptl':
            rowlabels[l] = 'D18-Particle'
        elif rowlabels[l] == 'hisubhalo':
            rowlabels[l] = 'D18-Subhalo'
        elif rowlabels[l] == 'galaxy':
            rowlabels[l] = 'Galaxies'
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
    
def fieldnameR_simResolutionC_box(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 1,
            border = 1):
    row_prop = 'fieldname'
    column_prop = 'sim_resolution'
    panel_prop = 'box'
    
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, panel_prop))
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, 'pk')
    pres = figArr[0,0]
    linelabels = {}
    for i in pres:
        box = i.getProp('box')
        linelabels[box] = '%d$^3$ (Mpc/h)$^3$'%round(box) 

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
    
def fieldnameR_boxC_simResolution(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 1,
            border = 1):
    row_prop = 'fieldname'
    column_prop = 'box'
    panel_prop = 'sim_resolution'
    
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, panel_prop))
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, 'pk')

    linelabels = {'high':'High', 'medium':'Medium', 'low':'Low'}
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
    

def fieldnameR_spaceC_gridResolution(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 1,
            border = 1):
    row_prop = 'fieldname'
    column_prop = 'space'
    panel_prop = 'grid_resolution'
    
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, panel_prop))
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, 'pk')

    linelabels = {}
    pres = figArr[0,0]
    for i in pres:
        gr = i.getProp('grid_resolution')
        linelabels[gr] = '%d$^3$ Bins'%gr

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