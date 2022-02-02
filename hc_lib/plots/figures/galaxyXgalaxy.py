from hc_lib.plots.fig_lib import FigureLibrary

def redshiftR_spaceC_color(rlib, iprops, rmprops, savePath = '', panel_length = 3, panel_bt = 0.25,
            border = 1):
    """
    Basic plot, shows how the pk of the red and blue galaxies change over time in both redshift
    and real space.
    """
    row_prop = 'redshift'
    column_prop = 'space'
    panel_prop = 'color'
    
    print('making %sR_%sC_%s figure...'%(row_prop, column_prop, panel_prop))
    figArr, rowlabels, collabels = rlib.organizeCrossFigure(iprops, row_prop, column_prop, 'pk', 1, rmprops, check = [0,0])
    rlib.tohdf5(figArr, savePath+'redshiftR_spaceC_color.hdf5', ['redshift', 'color', 'snapshot','space'])
    # linelabels = {'vn':'VN18-Particle', 'hiptl':'hiptl', 'hisubhalo':'hisubhalo'}
    # colors = {'vn':'green'}
    # flib = FigureLibrary(figArr)

    # flib.createFig(panel_length, panel_bt, border, border)
    # flib.plotLines(panel_prop, linelabels, colors)
    # # combining the lines
    # flib.fillLines('hisubhalo', label='D18-Subhalo', color='orange')
    # flib.fillLines('hiptl', label='D18-Particle', color='blue')
    # flib.addRowLabels(rowlabels)
    # flib.addColLabels(collabels)
    # flib.logAxis('both')

    # flib.removeDefaultTickLabels()
    # flib.changeTickDirection()
    # flib.xLimAdjustToNyquist()
    # flib.flushYAxisToData()
    # flib.matchAxisLimits()
    # flib.defaultAxesLabels()
    # flib.addLegend()
    # flib.printIprops(iprops)

    # if savefig, then save it, otherwise return it

    # if not savePath == '':
    #     # flib.saveFig(savePath, row_prop, column_prop, panel_prop)
    #     return
    # else:
    #     return flib
    return
