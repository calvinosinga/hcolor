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
    def __init__(self, figArr):
        self.fig = None
        self.figArr = figArr
        self.panels = None
        self.dim = figArr.shape
        return

    def createFig(self, panel_length, panel_bt, xborder, yborder):
        nrows = self.dim[0]
        ncols = self.dim[1]
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
        self.panel_length = panel_length
        self.panel_bt = panel_bt
        self.xborder = xborder
        self.yborder = yborder
        self.figsize = [figwidth, figheight]
        return

    def getFig(self):
        return self.fig, self.panels
    
    def plotLines(self, panel_prop, labels = None, colors = None, linestyles = None):
        dim = self.dim
        default_color_cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
        pprop = panel_prop
        lines = np.empty_like(self.figArr, dtype=object)

        def _plot_one_panel_rc(rc_panel):
            """
            Plots a panel when the results to be plotted (rc_panel)
            is a list of ResultContainer objects. This is default.
            """
            lines_for_panel = []
            for r in range(len(rc_panel)):
                r_container = rc_panel[r]
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
            
            return lines_for_panel
        
        def _plot_one_panel_dict(dict_panel):
            """
            Makes plots for a panel if given a dictionary - expected to occur when some post-analysis
            step was completed, like calculating redshift distortion.
            """
            lines_for_panel = []
            keys = list(dict_panel.keys())
            for r in range(len(dict_panel)):

                x = dict_panel[keys[r]][0]
                y = dict_panel[keys[r]][1]

                if labels is None:
                    l_lab = keys[r]
                else:
                    l_lab = labels[keys[r]]

                if colors is None:
                    l_c = default_color_cycle[r]
                else:
                    l_c = colors[keys[r]]

                if linestyles is None:    
                    l_ls = '-'
                else:
                    l_ls = linestyles[keys[r]]

                lines_for_panel.append(plt.plot(x, y, label = l_lab, color = l_c, 
                        linestyle = l_ls))
            
            return lines_for_panel

        for i in range(dim[0]):
            for j in range(dim[1]):
                p = self.panels[i][j]
                p.tick_params(which='both', direction = 'in')

                results_for_panel = self.figArr[i, j]
                plt.sca(p)
                
                # if figlib adds distortions or variance,
                # those results are stored as a dictionary
                # rather than a list of ResultContainers.
                # Thus, it requires a different way to plot them
                if not isinstance(results_for_panel, dict):
                    lines[i, j] = _plot_one_panel_rc(results_for_panel)
                else:
                    lines[i, j] = _plot_one_panel_dict(results_for_panel)
                
        self.lines = lines
        return lines
    
    def addRedshiftDistortion(self, real_slc, redshift_slc, panel_prop):
        """
        Adds a column or row that displays the redshift distortion
        of the results. The panel results are stored as dictionaries,
        as the ResultContainers require input not accessible for figlib.

        Changing the implementation of ResultContainers would mean that
        I would need to rerun everything since these are created during
        the analysis step, and I wanted to have figlib handle everything
        in the post-analysis step.

        This should be done BEFORE the create_fig method.
        """
        real_results = self.figArr[real_slc]
        redshift_results = self.figArr[redshift_slc]

        distArr = np.empty_like(real_results, dtype=object)
        
        # iterate over each panel in the results
        for i in range(len(real_results)):
            
            real_panel = real_results[i]
            red_panel = redshift_results[i]
            temp = {}

            # iterate over each result in the panel
            for j in range(len(real_panel)):
                
                wavenum, realpk, z = real_panel[j].getValues()
                line_prop = real_panel[j].props[panel_prop]
                for k in range(len(red_panel)):
                    # if the two have the same within-panel property, they
                    # should be matched up and given a distortion value
                    if line_prop == red_panel[j].props[panel_prop]:
                        wavenum, redpk, z = red_panel[j].getValues()

                temp[line_prop] = np.array([wavenum, realpk/redpk])
            
            distArr[i] = temp
        
        
        # find which axis to concatenate along (should only be two options, for 2D array)
        
        
        if distArr.shape == self.dim[0]:
            concat_ax = 0
        else:
            concat_ax = 1

        concat_dim = [-1, -1]
        concat_dim[concat_ax] = 1 
        
        distArr = np.reshape(distArr, concat_dim)
        self.figArr = np.concatenate((self.figArr, distArr), axis=concat_ax)
        self.dim = self.figArr.shape

        # making a list of the indices that the distortion panels are at
        if concat_ax == 0:
            dist_idx_list = [(self.dim[0]-1,i) for i in range(self.dim[1])]
        else:
            dist_idx_list = [(i, self.dim[1]-1) for i in range(self.dim[0])]
            
        return dist_idx_list

    # TODO: add variance
    
    def getLines(self):
        return self.lines
    
    def printIprops(self, iprops, fsize=6):
        outstr = r''
        for k, v in iprops.items():
            outstr += k + ': ' + str(v) + '; '
        self.fig.suptitle(outstr, fontsize = fsize, wrap = True, usetex = False)
        return
        
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
        if not panel_exceptions:
            panel_exceptions = self._defaultTickLabelPanelExceptions('y')
        self._removeTickLabels('y', panel_exceptions)
        return
    
    def _defaultTickLabelPanelExceptions(self, axis):
        if axis == 'y':
            return [(i, 0) for i in range(self.dim[0])]
        elif axis == 'x':
            return [(self.dim[0]-1, i) for i in range(self.dim[1])]
        else:
            return
        
    def removeXTickLabels(self, panel_exceptions = []):
        if not panel_exceptions:
            panel_exceptions = self._defaultTickLabelPanelExceptions('x')
        
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
    
    def axisLabel(self, text, axis, pos = [], fsize = 16, rotation = ''):
        posdict = {}
        if axis == 'x':
            if rotation == '':
                rotation = 'horizontal'
            posdict['x'] = [0.5, self.yborder[1]/3/self.figsize[1]]
        elif axis == 'y':
            if rotation == '':
                rotation = 'vertical'
            
            posdict['y'] = [self.xborder[0]/3/self.figsize[0], 0.5]
        
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
                    xmin, xmax = plt.xlim()
                    nyq = xmax
                    mink = np.inf
                    for r in res_container_list:
                        if not isinstance(res_container_list, dict):
                            
                            nyq_temp = r.props['grid_resolution'] * np.pi / r.props['box']
                            if nyq_temp < nyq:
                                nyq = nyq_temp
                            wavenum, pk, z = r.getValues()

                            if mink > np.min(wavenum):
                                mink = np.min(wavenum)

                    if not mink == np.inf:
                        plt.xlim(mink, nyq)
                    
                    else:
                        plt.xlim(xmin, nyq)
        self.matchAxisLimits(which='x', panel_exceptions=panel_exceptions)
        return
    
    def flushYAxisToData(self, result_type = 'pk'):
        for i in range(self.dim[0]):
            for j in range(self.dim[1]):
                p = self.panels[i][j]
                ylim = [np.inf, -np.inf]
                plt.sca(p)
                res_container_list = self.figArr[i, j]
                xmin, xmax = plt.xlim()

                if result_type == 'pk':
                    for r in res_container_list:
                        if not isinstance(res_container_list, dict):
                            wavenum, pk, z = r.getValues()
                        else:
                            wavenum = res_container_list[r][0]
                            pk = res_container_list[r][1]

                        max_idx = np.argmax(wavenum > xmax)
                        min_idx = np.argmax(wavenum < xmin)
                        
                        ymin = np.min(pk[min_idx:max_idx])
                        ymax = np.max(pk[min_idx:max_idx])
                        
                        if ymin < ylim[0]:
                            ylim[0] = ymin
                        if ymax > ylim[1]:
                            ylim[1] = ymax
                    plt.ylim(ylim[0], ylim[1])
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
        xlims = [-np.inf, np.inf]
        for i in range(dim[0]):
            for j in range(dim[1]):
                if not (i, j) in panel_exceptions:
                    p = self.panels[i][j]
                    plt.sca(p)
                    ymin, ymax = plt.ylim()
                    xmin, xmax = plt.xlim()
                    # for the y-axis, we want the largest max, smallest min
                    # in order to encompass the most data
                    if ymin < ylims[0]:
                        ylims[0] = ymin
                    if ymax > ylims[1]:
                        ylims[1] = ymax
                    # for the x-axis, we want the smallest max, largest min
                    # so no panel includes bad data
                    if xmin > xlims[0]:
                        xlims[0] = xmin
                    if xmax < xlims[1]:
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
            
    def saveFig(self, dir_path, rowp, colp, panelp, suffix = ''):
        outstr = '%sR_%sC_%s'%(rowp, colp, panelp)
        if not suffix == '':
            outstr += '_' + suffix 
        plt.savefig(dir_path + outstr + '.png')
        return
