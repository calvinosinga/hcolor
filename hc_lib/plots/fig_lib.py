import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.gridspec as gspec
import copy
mpl.rcParams['text.usetex'] = True

class FigureLibrary():
    def __init__(self, figArr):
        self.fig = None
        self.figArr = figArr
        self.panels = None
        self.dim = figArr.shape
        return

    def createFig(self, panel_length, panel_bt, xborder, yborder,
                colorbar = False):
        nrows = self.dim[0]
        ncols = self.dim[1]

        if colorbar:
            ncols += 1
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
                wspace=panel_bt[0]*ncols/figwidth, hspace=panel_bt[1]*nrows/figheight)
        
        # making panels list
        panels = []
        for i in range(self.dim[0]):
            col_panels = []
            for j in range(self.dim[1]):
                col_panels.append(fig.add_subplot(gs[i, j]))
                    
            panels.append(col_panels)
        
        if colorbar:
            self.cax = fig.add_subplot(gs[:, -1])
        else:
            self.cax = np.empty_like(self.figArr, dtype=object)
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
    
    def texStr(self, instr):
        if isinstance(instr, str):
            instr = instr.replace('_','\_')
        return instr

    def plotLines(self, panel_prop, labels = None, colors = None, linestyles = None):
        dim = self.dim
        default_color_cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
        pprop = panel_prop

        def _plot_one_panel_rc(rc_panel):
            """
            Plots a panel when the results to be plotted (rc_panel)
            is a list of ResultContainer objects. This is default.
            """
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
                
                plt.plot(x, y, label = self.texStr(l_lab), color = l_c, 
                        linestyle = l_ls)
            
            return
        
        def _plot_one_panel_dict(dict_panel):
            """
            Makes plots for a panel if given a dictionary - expected to occur when some post-analysis
            step was completed, like calculating redshift distortion.
            """
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
                
                plt.plot(x, y, label = self.texStr(l_lab), color = l_c, 
                        linestyle = l_ls)
            
            return

        for i in range(dim[0]):
            for j in range(dim[1]):
                p = self.panels[i][j]

                results_for_panel = self.figArr[i, j]
                plt.sca(p)
                
                # if figlib adds distortions or variance,
                # those results are stored as a dictionary
                # rather than a list of ResultContainers.
                # Thus, it requires a different way to plot them
                if not isinstance(results_for_panel, dict):
                    _plot_one_panel_rc(results_for_panel)
                else:
                    _plot_one_panel_dict(results_for_panel)

        return
    
    def fillLines(self, match_label, label = '', color = 'blue', 
                opacity = 0.55, dark_edges = False, except_panels = []):
        """
        For each line that has a label that is in match_label, the area between
        the lines is filled in and then the lines are removed from the plot.
        """
        
        for i in range(self.dim[0]):
            for j in range(self.dim[1]):
                if (i, j) not in except_panels:
                    p = self.panels[i][j]
                    plt.sca(p)
                    lines = p.get_lines()
                    # get the ymax/ymin of the lines
                    ymin = None
                    ymax = None
                    xdata = None
                    for l in lines:
                        if l.get_label() in match_label:
                            temp = l.get_ydata()
                            
                            if ymin is None:
                                ymin = temp
                                ymax = temp
                                xdata = l.get_xdata()
                            else:
                                ymin = np.minimum(ymin, temp)
                                ymax = np.maximum(ymax, temp)
                                if not xdata == l.get_xdata():
                                    print('failed xdata check, not the same')
                                    print(xdata)
                                    print(l.get_xdata())
                            
                            # since this will now be included in the
                            # filled area, remove it from the plot
                            l.set_visible(False)
                            
                    
                    # now make the plot
                    plt.fill_between(xdata, ymin, ymax, color=color, label=label,
                                alpha = opacity)
                            
                    if dark_edges:
                        plt.plot(xdata, ymin, color=color)
                        plt.plot(xdata, ymax, color=color)
                                        
        return

    def plotSlices(self):
        slices = np.empty_like(self.figArr, dtype=object)
        for i in range(self.dim[0]):
            for j in range(self.dim[1]):
                p = self.panels[i][j]

                if len(self.figArr[i, j]) == 1:
                    print('needs only one slice in order to plot...')
                pslice = self.figArr[i, j][0]

                plt.sca(p)

                x, y, mass = pslice.getValues()
                extent=(np.min(x), np.max(x), np.min(y), np.max(y))

                im = plt.imshow(mass, extent=extent, origin='lower')
                slices[i, j] = [im]

        
        self.plots = slices
        return
    
    def plot2D(self, maxks = [5, 5]):
        
        for i in range(self.dim[0]):
            for j in range(self.dim[1]):
                p = self.panels[i, j]
                plt.sca(p)
                # should only be one result in list
                result = self.figArr[i, j][0]
                kpar, kper, pk = result.getValues()
                kpar = np.unique(kpar)
                kper = np.unique(kper)
                paridx = np.where(kpar>maxks[0])[0][0]
                peridx = np.where(kper>maxks[1])[0][0]

                KPAR, KPER = np.meshgrid(kpar[:paridx], kper[:peridx])
                extent = (0,kpar[paridx-1],0,kper[peridx-1])
                plt.imshow(pk[:paridx, :peridx], extent=extent, origin='lower')
                
        return
    
    def addContours(self, color = 'k', maxks = [5,5], has_cax = False):
        for i in range(self.dim[0]):
            for j in range(self.dim[1]):
                p = self.panels[i, j]
                plt.sca(p)
                result = self.figArr[i, j][0]

                kpar, kper, pk = result.getValues()
                kpar = np.unique(kpar)
                kper = np.unique(kper)
                paridx = np.where(kpar>maxks[0])[0][0]
                peridx = np.where(kper>maxks[1])[0][0]

                KPAR, KPER = np.meshgrid(kpar[:paridx], kper[:peridx])

                if has_cax:
                    ticks = self.cax.get_yticks()
                    ylim = self.cax.get_ylim()


                else:
                    cbar = self.cax[i, j][0]
                    ticks = cbar.get_yticks()
                    ylim = cbar.get_ylim()
                
                plt.contour(KPAR, KPER, pk[:paridx,:peridx], vmin=ylim[0],
                        vmax=ylim[1], levels = ticks, colors=color, linestyle='-')

        return 
             
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
    def makeColorbars(self, shared_cax = False, cbar_label = '', except_panels = []):
        if shared_cax:
            self.matchColorbarLimits()
            self.logNormColorbar()
            self.assignColormaps('plasma', under='w')
            cbar = plt.colorbar(cax=self.cax)
            self.cax.set_aspect(8, anchor='W')
            cbar.set_label(cbar_label, rotation=270)
        else:
            for i in range(self.dim[0]):
                for j in range(self.dim[1]):
                    if (i,j) not in except_panels:
                        plt.sca(self.panels[i][j])
                        cbar = plt.colorbar(fraction=0.046, pad=0.04)
                        cbar.set_label(cbar_label, rotation=270)
                        self.cax[i, j] = [cbar]
                        

        return
    
    def assignColormaps(self, cmap_array, under = None, over = None):

        for i in range(self.dim[0]):
            for j in range(self.dim[1]):
                im = self.plots[i, j][0]
                ca = cmap_array[i, j]
                if isinstance(ca, str):
                    cmap = copy.copy(mpl.cm.get_cmap(ca))
                else:
                    cmap = ca
                
                if not under is None:
                    cmap.set_under(under)
                if not over is None:
                    cmap.set_over(over)
                
                im.set_cmap(cmap)
        
        return

    def logNormColorbar(self, vlim = [], panel_exceptions = []):
        for i in range(self.dim[0]):
            for j in range(self.dim[1]):
                if (i, j) not in panel_exceptions:
                    im = self.plots[i, j][0]
                    clim = im.get_clim()
                    if vlim:
                        im.set_norm(mpl.colors.LogNorm(vmin=vlim[0], vmax=vlim[1]))
                    else:
                        im.set_norm(mpl.colors.LogNorm(vmin=clim[0], vmax=clim[1]))
                    
        return
      
    def matchColorbarLimits(self, panel_exceptions = []):
        # get the limits
        vlim = [np.inf, -np.inf]
        for i in range(self.dim[0]):
            for j in range(self.dim[1]):
                if (i, j) not in panel_exceptions:
                    im = self.plots[i, j][0]
                    if vlim[0] > im.clim[0]: vlim[0]=im.clim[0] 
                    if vlim[1] < im.clim[1]: vlim[1]=im.clim[1]
                        
        for i in range(self.dim[0]):
            for j in range(self.dim[1]):
                if (i, j) not in panel_exceptions:
                    im = self.plots[i, j][0]
                    im.set_clim(tuple(vlim))

        return

    def printIprops(self, iprops, fsize=6):
        outstr = r''
        for k, v in iprops.items():
            outstr += k + ': ' + str(v) + '; '
        self.fig.suptitle(outstr, fontsize = fsize, wrap = True, usetex = False)
        return
        
    def addRowLabels(self, rowlabels, pos = (0.05, 0.05), fsize = 16):
        dim = self.dim
        print(rowlabels)
        for i in range(dim[0]):
            p = self.panels[i][0]
            plt.sca(p)
            print(self.texStr(rowlabels[i]))
            plt.text(pos[0], pos[1], self.texStr(rowlabels[i]), fontsize = fsize,
                        ha = 'left', va = 'bottom', transform = p.transAxes)
        return
    
    def addColLabels(self, collabels, fsize = 16):
        dim = self.dim
        for j in range(dim[1]):
            p = self.panels[0][j]
            plt.sca(p)
            p.xaxis.set_label_position('top')
            plt.xlabel(self.texStr(collabels[j]), fontsize = fsize)
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

    def changeTickDirection(self, which = 'both', direction = 'in', panel_exceptions=[]):
        for i in range(self.dim[0]):
            for j in range(self.dim[1]):
                if (i,j) not in panel_exceptions:
                    self.panels[i][j].tick_params(which=which, direction = direction)
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
        
        self.fig.text(pos[0], pos[1], self.texStr(text), ha = 'center', va = 'center',
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

    def defaultPKAxesLabels(self, dim = 1):
        if dim == 1:
            xlab = r'k (Mpc/h)$^{-1}$'
            ylab = r'P(k) (Mpc/h)$^{-3}$'
        elif dim == 2:
            xlab = r"kpar (h/Mpc)"
            ylab = r"kper (h/Mpc)"
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
