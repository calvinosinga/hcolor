import matplotlib.pyplot as plt
import matplotlib as mpl
from hc_lib.plots.fig_lib import FigureLibrary

def redshiftR_spaceC_model(rlib, iprops, savefig = True, panel_length = 3, panel_bt = 0.25,
            border = 1, fsize = 16):
    
    figArr, rowlabels, collabels = rlib.organizeFigure(iprops, 'redshift', 'space', 'pk')
    
    print(figArr.shape)
    print(rowlabels)
    print(collabels)

    print(len(figArr[0, 0]))
    #for i in figArr[0, 0]:
    #    print(i.props)
    # make the figure
    dim = figArr.shape
    flib = FigureLibrary()
    flib.createFig(panel_length, dim[0], dim[1], panel_bt, border, border)
    # if savefig, then save it, otherwise return it

    lines = flib.plotLines(figArr)
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
