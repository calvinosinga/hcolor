import matplotlib.pyplot as plt
import matplotlib as mpl
from hc_lib.plots.fig_lib import FigureLibrary

def redshiftR_spaceC_model(rlib, iprops, savefig = True, panel_length = 3, panel_bt = 0.25,
            border = 1):
    
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, 'redshift', 'space', 'pk')
    
    rowlabels = ['z=%.1f'%i for i in rowlabels]
    collabels = [i.capitalize() for i in collabels]

    dim = figArr.shape
    flib = FigureLibrary()
    flib.createFig(panel_length, dim[0], dim[1], panel_bt, border, border)
    # if savefig, then save it, otherwise return it

    flib.plotLines(figArr, 'model')
    flib.addRowLabels(rowlabels)
    flib.addColLabels(collabels)
    flib.logAxis()
    flib.removeDefaultTickLabels()
    flib.xLimAdjustToNyquist()
    flib.matchAxisLimits()
    flib.defaultPKAxesLabels()
    flib.addLegend()
    flib.printIprops(iprops)
    plt.savefig('trial_run.png')
    return

def modelR_spaceC_map(rlib, iprops, savefig = True):
    return

def redshiftR_modelC_space(rlib, iprops, savefig = True):
    return

def modelR_spaceC_box(rlib, iprops, savefig = True):
    return

def modelR_spaceC_gridResolution(rlib, iprops, savefig = True):
    return

def modelR_spaceC_simResolution(rlib, iprops, savefig = True):
    return

def redshiftR_mapC_axis(rlib, iprops, savefig = True):
    return
