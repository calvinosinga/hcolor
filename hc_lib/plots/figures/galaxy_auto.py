from hc_lib.plots.fig_lib import FigureLibrary
import numpy as np

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

    linelabels = {'blue' : 'Blue Galaxies', 'red' : 'Red Galaxies', 'resolved':'All Galaxies',
            'all':'All Subhalos'}
    colors = {'blue':'blue', 'red':'red', 'resolved':'green', 'all':'black'}
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
    flib.flushYAxisToData(panel_exceptions = dist_panels_idx_list)
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

def redshiftR_colorC_space(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 1,
            border = 1):
    """
    Basic plot, shows how the pk of the red and blue galaxies change over time in both redshift
    and real space.
    """
    row_prop = 'redshift'
    column_prop = 'color'
    panel_prop = 'space'
    
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, panel_prop))
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, 'pk')

    linelabels = {'real':'Real Space', 'redshift':'Redshift Space'}
    linecolors = {'real':'blue', 'redshift':'red'}
    #print(figArr.shape)
    flib = FigureLibrary(figArr)
    # add distortion panels

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

def colorR_spaceC_redshift(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 1,
            border = 1):
    """
    More easily visualize the redshift evolution of the power spectrum.
    """
    row_prop = 'color'
    column_prop = 'space'
    panel_prop = 'redshift'
    
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, panel_prop))
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, 'pk')

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

def colorR_spaceC_grid_resolution(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 1,
            border = 1):
    """
    Comparing different grid resolutions.
    """
    row_prop = 'color'
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

def colorR_spaceC_sim_resolution(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 1,
            border = 1):
    """
    Comparing simulation resolution
    """
    row_prop = 'color'
    column_prop = 'space'
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

def colorR_spaceC_box(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 1,
            border = 1):
    """
    Compare Box volume
    """
    row_prop = 'color'
    column_prop = 'space'
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

def colorR_boxC_simResolution(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 1,
            border = 1):
    """
    Compare Box volume
    """
    row_prop = 'color'
    column_prop = 'box'
    panel_prop = 'sim_resolution'
    
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, panel_prop))
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, 'pk')
    collabels = ['%d$^3$ (Mpc/h)$^3$'%round(i) for i in collabels]
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
    linelabels = {'stmass':'Stellar Particles', 'total':'All Particles'}
    only_props = {'color_cut':[None, '0.60']}
    figArr = rlib.removeResults(figArr, only_props)
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
    
def fieldnameR_colorC_color_cut(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 0.25,
            border = 1):
    """
    Visualize how the color_cut used affects the pk for the color, with and without
    dust.
    """
    row_prop = 'fieldname'
    column_prop = 'color'
    panel_prop = 'color_cut'
    
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, panel_prop))
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, 'pk')


    colcuts = rlib.getVals('pk', 'color_cut', iprops)
    linelabels = {}
    linests = {}
    for c in colcuts:
        if c is None:
            continue
        elif '0' == c[0]:
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
    flib.addRowLabels(rowlabels)
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
        

def redshiftR_colorC_axis(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 0.25,
            border = 1):
    """
    Measuring the effect of the line of sight on the redshift-space power spectrum
    """
    iprops['space'] = 'redshift'
    row_prop = 'redshift'
    column_prop = 'color'
    panel_prop = 'axis'
    
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, panel_prop))
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, 'pk')

    #for r in range(len(rowlabels)):
    #    if rowlabels[r] == 'galaxy':
    #        rowlabels[r] = 'Fiducial'
    #    if rowlabels[r] == 'galaxy_dust':
    #        rowlabels[r] = 'Dust Model'

    linelabels = {0 : 'X-axis', 1 : 'Y-axis', 2:'Z-axis'}
    #print(figArr.shape)
    flib = FigureLibrary(figArr)


    flib.createFig(panel_length, panel_bt, border, border)
    flib.plotLines(panel_prop, labels=linelabels)
    flib.addRowLabels(rowlabels)
    flib.addColLabels(collabels)
    flib.logAxis()

    flib.removeXTickLabels()
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

def redshiftR_colorC_2D(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 0.25,
            border = 1):
    """
    Visualize how the redshift space distortions change with redshift for different
    galaxy colors.
    """
    row_prop = 'redshift'
    column_prop = 'color'
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, '2D'))
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, '2Dpk')

    cmap_arr = np.empty_like(figArr, dtype=object)
    cmap_arr[:,:] = 'plasma'
    flib = FigureLibrary(figArr)
    
    flib.createFig(panel_length, panel_bt, border, border, True)
    flib.plot2D()
    flib.makeColorbars('P(k$_\parallel$, k$_\perp$) (Mpc/h)$^{-3}$', vlim=[10**2,10**4])

    flib.addContours()

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
    
def axisR_colorC_2D(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 0.25,
            border = 1):
    """
    Visualize how different line-of-sight affects the redshift space distortion.
    """
    row_prop = 'axis'
    column_prop = 'color'
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, '2D'))
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, '2Dpk')

    cmap_arr = np.empty_like(figArr, dtype=object)
    cmap_arr[:,:] = 'plasma'
    flib = FigureLibrary(figArr)

    flib.createFig(panel_length, panel_bt, border, border, True)
    flib.plot2D()
    flib.makeColorbars('P(k) (Mpc/h)$^{-3}$', vlim=[10**2, 10**4])

    # flib.logNormColorbar()
    # flib.matchColorbarLimits()
    # flib.assignColormaps(cmap_arr, under='w')

    flib.addContours()

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

def make_histograms(rlib, iprops, savePath='', panel_length = 3, panel_bt = 1.25,
            border = 1):
    rowp = 'redshift'
    colp = 'fieldname'
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, rowp, colp, 'hist')
    flib = FigureLibrary(figArr)
    for c in range(len(collabels)):
        if collabels[c] == 'galaxy':
            collabels[c] = 'Fiducial'
        elif collabels[c] == 'galaxy_dust':
            collabels[c] = 'With Dust'
    flib.createFig(panel_length, panel_bt, border, border)
    flib.plotHists()
    flib.addRowLabels(rowlabels, is2D = True)
    flib.addColLabels(collabels)
    flib.changeTickDirection()
    flib.axisLabel('Log (M$_*$/M$_\odot$)', 'x')
    flib.axisLabel('g-r (magnitude)', 'y')
    flib.makeColorbars(cbar_label = 'Count (Galaxies)')
    cmap_arr = np.empty_like(figArr, dtype=object)
    cmap_arr[:,:]= 'viridis'
    flib.assignColormaps(cmap_arr, 'w')
    flib.logNormColorbar(vlim=[1,5e2])
    
    if not savePath == '':
        flib.saveFig(savePath, rowp, colp, 'hist')
        return None
    else:
        return flib
    return

####################SAVE FOR LATER#######################################
def spaceR_colorC_mas(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 0.25,
            border = 1):
    """
    Visualize the effect of using CIC or CICW for the mass-assignment scheme.
    (Ignore for now)
    """
    row_prop = 'space'
    column_prop = 'color'
    panel_prop = 'mas'
    
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, panel_prop))
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, 'pk')

    only_props = {'color_cut':[None, '0.60']}
    figArr = rlib.removeResults(figArr, only_props)
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

def color_cutR_colorC_gal_res(rlib, iprops, savePath = '', panel_length = 3, panel_bt = 0.25,
            border = 1):
    """
    Visualize how the color_cut used affects the pk for the color.
    (Ignore for now)
    """
    row_prop = 'color_cut'
    column_prop = 'color'
    panel_prop = 'gal_res'
    
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, panel_prop))
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, row_prop, column_prop, 'pk')

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
