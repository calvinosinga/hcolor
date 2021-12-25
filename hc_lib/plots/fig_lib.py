import pickle as pkl
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.gridspec as gspec
import copy
from mpl_toolkits.axes_grid1 import make_axes_locatable
mpl.rcParams['text.usetex'] = True

class FigureLibrary():
    def __init__(self):
        self.fig = None
        self.panels = None
        return

    def createFig(self, panel_length, nrows, ncols, panel_bt, xborder, yborder):
        # border input can be either a list or single number
        if isinstance(xborder, float) or isinstance(xborder, int):
            xborder = [xborder, xborder]
        if isinstance(yborder, float) or isinstance(yborder, int):
            yborder = [yborder, yborder]
        if isinstance(panel_bt, float) or isinstance(panel_bt, int):
            panel_bt = [panel_bt, panel_bt]
        # creating Figure object

        figwidth = panel_length * ncols + panel_bt[0] * (ncols - 1) + \
                xborder[0] + xborder[1]
        figheight = panel_length * nrows + panel_bt[1] * (nrows - 1) + \
                yborder[0] + yborder[1]
        
        fig = plt.figure(figsize=(figwidth, figheight))

        # creating gridspec
        gs = gspec.GridSpec(nrows, ncols)
        plt.subplots_adjust(left= xborder[0]/figwidth, right=1-xborder[1]/figwidth,
                top=1-yborder[1]/figheight, bottom=yborder[0]/figheight,
                wspace=panel_bt[0], hspace=panel_bt[1])
        
        # making panels list
        panels = []
        for i in range(nrows):
            col_panels = []
            for j in range(ncols):
                col_panels.append(fig.add_subplot(gs[i,j]))
            panels.append(col_panels)
        
        self.fig = fig
        self.panels = panels
        return

    def getFig(self):
        return self.fig, self.panels
    
    def plotLines(self, figArr):
        dim = figArr.shape
        lines = np.empty_like(figArr, dtype=object)
        for i in range(dim[0]):
            for j in range(dim[1]):
                p = self.panels[i][j]
                results_for_panel = figArr[i, j]
                lines_for_panel = []
                self.fig.sca(p)
                for r in results_for_panel:
                    x, y, z = r.getValues()
                    lines_for_panel.append(plt.plot(x, y))
                lines[i, j] = lines_for_panel
        self.lines = lines
        self.figArr = figArr
        return lines
    
    def addRowLabels(self, rowlabels, pos = (0.05, 0.05)):
        dim = figArr.shape
        for i in range(dim[0]):
            plt.sca(self.panels[i][0])
            plt.
