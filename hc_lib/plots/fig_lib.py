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
        self.dim = [nrows, ncols]
        self.panel_length = panel_length
        self.panel_bt = panel_bt
        self.xborder = xborder
        self.yborder = yborder
        self.figsize = [figwidth, figheight]
        return

    def getFig(self):
        return self.fig, self.panels
    
    def plotLines(self, figArr, panel_prop, labels = None, colors = None, linestyles = None):
        dim = self.dim
        default_color_cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
        pprop = panel_prop
        lines = np.empty_like(figArr, dtype=object)
        for i in range(dim[0]):
            for j in range(dim[1]):
                p = self.panels[i][j]
                p.tick_params(which='both', direction = 'in')

                results_for_panel = figArr[i, j]
                lines_for_panel = []
                plt.sca(p)
                for r in range(len(results_for_panel)):
                    r_container = results_for_panel[r]
                    x, y, z = r_container.getValues()


                    if labels is None:
                        l_lab = r_container.props[pprop]
                    else:
                        l_lab = labels[r_container.props[pprop]]

                    if colors is None:
                        l_c = default_color_cycle[r]
                    else:
                        l_c = colors[r.props[pprop]]

                    if linestyles is None:    
                        l_ls = '-'
                    else:
                        l_ls = linestyles[r.props[pprop]]
                    
                    lines_for_panel.append(plt.plot(x, y, label = l_lab, color = l_c, 
                                linestyle = l_ls))
                
                lines[i, j] = lines_for_panel
        self.lines = lines
        self.figArr = figArr
        return lines
    
    def getLines(self):
        return self.lines
    

    def addRowLabels(self, rowlabels, pos = (0.05, 0.05), fsize = 16):
        dim = self.dim
        for i in range(dim[0]):
            p = self.panels[i][0]
            plt.sca(p)
            plt.text(pos[0], pos[1], rowlabels[i], fontsize = fsize,
                        ha = 'left', va = 'bottom', transform = p.transAxes)
        return
    
    def addColLabels(self, collabels, fsize = 16):
        dim = self.dim
        for j in range(dim[1]):
            p = self.panels[0][j]
            plt.sca(p)
            p.xaxis.set_label_position('top')
            plt.xlabel(collabels[j], fontsize = fsize)
        return
    
    def removeYTickLabels(self, panel_exceptions = []):
        dim = self.dim
        if not panel_exceptions:
            panel_exceptions = [(i, dim[1]-1) for i in range(dim[0])]
        
        self._removeTickLabels('y', panel_exceptions)
        return
    
    def removeXTickLabels(self, panel_exceptions = []):
        dim = self.dim
        if not panel_exceptions:
            panel_exceptions = [(dim[0]-1, i) for i in range(dim[1])]
        
        self._removeTickLabels('x', panel_exceptions)
        return
    
    def removeDefaultTickLabels(self):
        self.removeXTickLabels()
        self.removeYTickLabels()
        return
    
    def _removeTickLabels(self, axis, panel_exceptions = []):
        dim = self.dim
        
        for i in range(dim[0]):
            for j in range(dim[1]):
                if (i, j) not in panel_exceptions:
                    p = self.panels[i][j]
                    if axis == 'y':
                        p.yaxis.set_ticklabels([])
                    elif axis == 'x':
                        p.xaxis.set_ticklabels([])
        return

    def logAxis(self, which = 'both', panel_exceptions = []):
        dim = self.dim

        for i in range(dim[0]):
            for j in range(dim[1]):
                if (i, j) not in panel_exceptions:
                    p = self.panels[i][j]
                    plt.sca(p)
                    if which == 'both':
                        plt.loglog()
                    elif which == 'y':
                        plt.yscale('log')
                    elif which == 'x':
                        plt.xscale('log')
        
        return
    
    def axisLabel(self, text, axis, pos = [], fsize = 16):
        posdict = {}
        if axis == 'x':
            rotation = 'horizontal'
            posdict['x'] = [0.5, self.yborder[1]/3/self.figsize[0]]
        elif axis == 'y':
            rotation = 'vertical'
            posdict['y'] = [self.xborder[0]/3/self.figsize[1], 0.5]
        
        if not pos:
            pos = posdict[axis]
        

        self.fig.text(pos[0], pos[1], text, ha = 'center', va = 'center',
                    fontsize = fsize, rotation = rotation)
        return
    
    def addLegend(self, panel_idx = (0,0), loc = 'upper right'):
        p = self.panels[panel_idx[0]][panel_idx[1]]
        plt.sca(p)
        plt.legend(loc = loc)
        return
    
    def xLimAdjustToNyquist(self, panel_exceptions = []):
        dim = self.dim

        for i in range(dim[0]):
            for j in range(dim[1]):
                if (i, j) not in panel_exceptions:
                    p = self.panels[i][j]
                    plt.sca(p)
                    res_container_list = self.figArr[i, j]
                    nyq = np.inf
                    for r in res_container_list:
                        nyq_temp = r.props['grid_resolution'] * np.pi / r.props['box']
                        if nyq_temp < nyq:
                            nyq = nyq_temp

                    xmin, xmax = plt.xlim()
                    plt.xlim(xmin, nyq)
                        
        return
    
    def defaultPKAxesLabels(self):
        xlab = r'k (Mpc/h)$^{-1}$'
        ylab = r'P(k) (Mpc/h)$^{-3}$'
        self.axisLabel(xlab, 'x')
        self.axisLabel(ylab, 'y')
        return
    
    def _getLimits(self, panel_exceptions = []):
        dim = self.dim
        ylims = [np.inf, -np.inf]
        xlims = [np.inf, -np.inf]
        for i in range(dim[0]):
            for j in range(dim[1]):
                if not (i, j) in panel_exceptions:
                    p = self.panels[i][j]
                    plt.sca(p)
                    ymin, ymax = plt.ylim()
                    xmin, xmax = plt.xlim()
                    if ymin < ylims[0]:
                        ylims[0] = ymin
                    if ymax > ylims[1]:
                        ylims[1] = ymax
                    if xmin < xlims[0]:
                        xlims[0] = xmin
                    if xmax > xlims[1]:
                        xlims[1] = xmax
        
        return xlims, ylims
                    

    def matchAxisLimits(self, which = 'both', panel_exceptions = []):
        xlim, ylim = self._getLimits(panel_exceptions)
        dim = self.dim
            
        for i in range(dim[0]):
            for j in range(dim[1]):
                if not (i, j) in panel_exceptions:
                    p = self.panels[i][j]
                    plt.sca(p)
                    if which == 'x' or which == 'both':
                        plt.xlim(xlim[0], xlim[1])
                    elif which == 'y' or which == 'both':
                        plt.ylim(ylim[0], ylim[1])
        
        return
            
