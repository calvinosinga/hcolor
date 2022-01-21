import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.gridspec as gspec
import copy
import illustris_python as il
mpl.rcParams['text.usetex'] = True

class FigureLibrary():
    def __init__(self, figArr):
        self.fig = None
        self.panels = None
        self.figArr = figArr
        
        self.dim = figArr.shape
        return

    def createFig(self, panel_length, panel_bt, xborder, yborder,
                colorbar_col = False):
        nrows = self.dim[0]
        ncols = self.dim[1]

        if colorbar_col:
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
        
        if colorbar_col:
            caxlist = []
            for i in range(nrows):
                caxlist.append(fig.add_subplot(gs[i, -1]))
            self.cax = caxlist
            self.has_cbar_col = True
        else:
            self.has_cbar_col = False
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

    def clf(self):
        plt.clf()
        return
    
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
                elif not str(r_container.props[pprop]) in labels:
                    l_lab = r_container.props[pprop]
                else:
                    l_lab = labels[r_container.props[pprop]]

                if colors is None:
                    l_c = default_color_cycle[r%len(default_color_cycle)]
                elif not str(r_container.props[pprop]) in colors:
                    l_c = default_color_cycle[r%len(default_color_cycle)]
                else:
                    l_c = colors[r_container.props[pprop]]

                if linestyles is None:    
                    l_ls = '-'
                elif not str(r_container.props[pprop]) in linestyles:
                    l_ls = '-'
                else:
                    l_ls = linestyles[r_container.props[pprop]]
                
                plt.plot(x, y, label = self.texStr(l_lab), color = l_c, 
                        linestyle = l_ls)
            
            return

        for i in range(dim[0]):
            for j in range(dim[1]):
                p = self.panels[i][j]

                results_for_panel = self.figArr[i, j]
                plt.sca(p)
                
                _plot_one_panel_rc(results_for_panel)


        return
    
    def fillLines(self, match_label, label = '', color = 'blue', 
                opacity = 0.55, dark_edges = False, except_panels = []):
        """
        For each line that has a panel_label that is in match_label, the area between
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
                            
                            # since this will now be included in the
                            # filled area, remove it from the plot
                            l.set_visible(False)
                            l.set_label('_nolegend_')

                    # now make the plot
                    plt.fill_between(xdata, ymin, ymax, color=color, label=label,
                                alpha = opacity)
                            
                    if dark_edges:
                        plt.plot(xdata, ymin, color=color)
                        plt.plot(xdata, ymax, color=color)
                                        
        return

    def plotSlices(self, plot_interp = None):
        
        for i in range(self.dim[0]):
            for j in range(self.dim[1]):
                p = self.panels[i][j]

                if not len(self.figArr[i, j]) == 1:
                    print('needs only one slice in order to plot...')
                pslice = self.figArr[i, j][0]

                plt.sca(p)

                xlim, ylim, mass = pslice.getValues()

                if not pslice.getProp('is_groupcat'):
                    plot_interp = None
                
                extent=(xlim[0], xlim[1], ylim[0], ylim[1])
                cmap = self.cmap_arr[i, j]
                norm = self.norm_arr[i, j]
                # x_bound, y_bound, mass = pslice.getValues()
                # extent=(x_bound[0], x_bound[1], y_bound[0], y_bound[1])
                
                plt.imshow(mass, cmap = cmap, norm = norm, aspect = 'auto', extent=extent, 
                            origin='lower', interpolation= plot_interp)
            
            if self.has_cbar_col:
                p = self.cax[i]
                cmap = self.cmap_arr[i,0]
                norm = self.norm_arr[i,0]
                p.set_aspect(12,anchor = 'W')
                self.fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), cax=p)
        return
    
    def plotHists(self, make_lines = True):
        for i in range(self.dim[0]):
            for j in range(self.dim[1]):
                p = self.panels[i][j]
                plt.sca(p)
                cmap = self.cmap_arr[i, j]
                norm = self.norm_arr[i, j]

                hist = self.figArr[i,j][0]
                xbins, ybins, counts = hist.getValues()
                counts = np.rot90(np.flip(counts, axis=0), 3)
                extent = (xbins[0], xbins[-1], ybins[0], ybins[-1])
                plt.imshow(counts, cmap = cmap, norm = norm, origin='lower', extent=extent, 
                            aspect = 'auto')
                if make_lines:
                    plt.plot([xbins[0], xbins[-1]], [0.6, 0.6], color='red')
                    plt.plot([xbins[0], xbins[-1]], [0.55, 0.55], color='red')
                    plt.plot([xbins[0], xbins[-1]], [0.5, 0.5], color='red', linestyle = ':')
                    plt.plot([xbins[0], xbins[-1]], [0.65, 0.65], color='red')
                    plt.plot([xbins[0], xbins[-1]], [0.7, 0.7], color='red', linestyle = ':')
                    #stmass bins already log
                    plt.plot(xbins, 0.65 + 0.02 * (xbins - 10.28), color='white', linestyle = '--')
        
        if self.has_cbar_col:
            p = self.cax[i]
            cmap = self.cmap_arr[i,0]
            norm = self.norm_arr[i,0]
            self.fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), cax=p)
            p.set_aspect(12, anchor='W')

        return
    
    def plot2D(self, maxks = [5, 5]):
        
        for i in range(self.dim[0]):
            for j in range(self.dim[1]):
                p = self.panels[i][j]
                cmap = self.cmap_arr[i,j]
                norm = self.norm_arr[i,j]
                plt.sca(p)
                # should only be one result in list
                result = self.figArr[i, j][0]
                if len(self.figArr[i, j]) > 1:
                    print('there are more 2dpk than there should be')
                KPAR, KPER, plotpk = self._get2DpkData(result, maxks)
                extent = (np.min(KPAR),np.max(KPAR),np.min(KPER),np.max(KPER))
                
                plt.imshow(plotpk, extent=extent, origin='lower', aspect = 'auto',
                            norm=norm, cmap=cmap)

            if self.has_cbar_col:
                p = self.cax[i]
                cmap = self.cmap_arr[i,0]
                norm = self.norm_arr[i,0]
                self.fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), cax=p)
                p.set_aspect(12, anchor = 'W')
        return
    

    def addContours(self, color = 'k', maxks = [5,5], cstep = 0.5):
        for i in range(self.dim[0]):
            for j in range(self.dim[1]):
                p = self.panels[i][j]
                norm = self.norm_arr[i,j]
                plt.sca(p)
                result = self.figArr[i, j][0]
                KPAR, KPER, plotpk = self._get2DpkData(result, maxks)

                levels = np.arange(int(norm.vmin), int(norm.vmax)+1, cstep)
                plt.contour(KPAR, KPER, plotpk, vmin=norm.vmin,
                        vmax=norm.vmax, levels = levels, colors=color,
                        linestyles='solid')

        return
    
    def _get2DpkData(self, result, maxks):
        kpar, kper, pk = result.getValues()

        kpar = np.unique(kpar)
        kper = np.unique(kper)
        # check to make sure kpar, kper are correct (kper should be longer)
        if len(kpar) > len(kper):
            print('have kpar and kper mixed up')

        paridx = np.where(kpar>maxks[0])[0][0]
        peridx = np.where(kper>maxks[1])[0][0]

        pk = np.reshape(pk, (len(kper), len(kpar)))
        plotpk = np.log10(pk[:paridx, :peridx])
        KPAR, KPER = np.meshgrid(kpar[:peridx], kpar[:paridx])
        return KPAR, KPER, plotpk

    def assign2DNorms(self, vlim_list = []):
        if not vlim_list:
            vlim_list = [[-2, 4] for i in range(self.dim[0])]
        norm_arr = np.empty_like(self.figArr, dtype = object)
        for i in range(self.dim[0]):
            for j in range(self.dim[1]):
                vlim = vlim_list[i]
                norm_arr[i,j] = mpl.colors.Normalize(vmin=vlim[0], vmax=vlim[1])
        self.norm_arr = norm_arr
        return

    def assignSliceNorms(self, vlim_list = []):
        if not vlim_list:
            vlim_list = [[2, 12.5] for i in range(self.dim[1])]
        norm_arr = np.empty_like(self.figArr, dtype = object)
        for i in range(self.dim[0]):
            for j in range(self.dim[1]):
                vlim = vlim_list[i]
                norm_arr[i,j] = mpl.colors.Normalize(vmin=vlim[0], vmax=vlim[1])
        self.norm_arr = norm_arr
        return
    
    def assignHistNorms(self, vlim_list = []):
        if not vlim_list:
            vlim_list = [[1, 5e2] for i in range(self.dim[1])]
        norm_arr = np.empty_like(self.figArr, dtype = object)

        for i in range(self.dim[0]):
            for j in range(self.dim[1]):
                vlim = vlim_list[i]
                norm_arr[i,j] = mpl.colors.LogNorm(vmin=vlim[0], vmax=vlim[1])
        self.norm_arr = norm_arr
        return
    
    def setNormArr(self, norm_arr):
        self.norm_arr = norm_arr
        return
 
    def setColorbarLabels(self, cbar_label='', labelpad = 20, ha = 'center', va='top',
                label_type = '', fsize = 16):
        if label_type == '2dpk':
            cbar_label = 'log P(k$_\parallel$, k$_\perp$) (Mpc/h)$^{-3}$'
        if label_type == 'slice':
            cbar_label = 'log M$_*$/M$_/odot$'
        for i in range(len(self.cax)):
            p = self.cax[i]
            plt.sca(p)
            p.set_ylabel(cbar_label, fontsize = fsize, labelpad = labelpad, ha = ha, va=va)
        return

     
    def assignColormaps(self, cmap_name = 'plasma', under = None, over = None):
        self.cmap_arr = np.empty_like(self.figArr)
        cmap = copy.copy(mpl.cm.get_cmap(cmap_name))
        if not under is None:
            cmap.set_under(under)
        if not over is None:
            cmap.set_over(over)
        
        self.cmap_arr[:,:] = cmap
        
        return

    def setCmapArr(self, cmap_arr):
        self.cmap_arr = cmap_arr
        return

    def printIprops(self, iprops, fsize=6):
        outstr = r''
        for k, v in iprops.items():
            outstr += k + ': ' + str(v) + '; '
        self.fig.suptitle(outstr, fontsize = fsize, wrap = True, usetex = False)
        return
        
    def addRowLabels(self, rowlabels, pos = (0.05, 0.05), fsize = 16, is2D = False,
                    color = 'black'):
        dim = self.dim
        if not is2D:
            
            for i in range(dim[0]):
                p = self.panels[i][0]
                plt.sca(p)
                plt.text(pos[0], pos[1], self.texStr(rowlabels[i]), fontsize = fsize,
                            ha = 'left', va = 'bottom', color = color, 
                            transform = p.transAxes)
        else:
            for i in range(dim[0]):
                p = self.panels[i][0]
                plt.sca(p)
                plt.ylabel(rowlabels[i], color=color, fontsize=fsize)
        return
    
    def addColLabels(self, collabels, fsize = 16, color='black'):
        dim = self.dim
        for j in range(dim[1]):
            p = self.panels[0][j]
            plt.sca(p)
            p.xaxis.set_label_position('top')
            plt.xlabel(self.texStr(collabels[j]), color = color, fontsize = fsize)
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
    
    def axisLabel(self, text, axis, pos = [], fsize = 16, rotation = '', usetex=True):
        posdict = {}
        if axis == 'x':
            if rotation == '':
                rotation = 'horizontal'
            if self.has_cbar_col:
                ncols = self.dim[1] # does not include cbar panel
                image_length = ncols * self.panel_length + \
                        self.panel_bt[0] * (ncols - 1)
                
                hpos = (0.5 * image_length + self.xborder[0]) / self.figsize[0]
            else:
                hpos = 0.5
            posdict['x'] = [hpos, self.yborder[1]/3/self.figsize[1]]
        elif axis == 'y':
            if rotation == '':
                rotation = 'vertical'
            
            posdict['y'] = [self.xborder[0]/3/self.figsize[0], 0.5]
        
        if not pos:
            pos = posdict[axis]
        
        if not usetex:
            text= self.texStr(text)
        
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
    
    def flushYAxisToData(self, result_type = 'pk', panel_exceptions = []):
        
        for i in range(self.dim[0]):
            for j in range(self.dim[1]):
                if (i, j) not in panel_exceptions:
                    p = self.panels[i][j]
                    plt.sca(p)
                    res_container_list = self.figArr[i, j]
                    xmin, xmax = plt.xlim()
                    ylim = [np.inf, -np.inf] # each panel is flushed individually, reset ylim vals
                    if result_type == 'pk':
                        for r in res_container_list:
                            # iterate through all the plots to find the data plotted
                            if not isinstance(res_container_list, dict):
                                wavenum, pk, z = r.getValues()
                            else:
                                wavenum = res_container_list[r][0]
                                pk = res_container_list[r][1]

                            max_idx = np.argmax(wavenum > xmax)
                            min_idx = np.argmax(wavenum < xmin)
                            
                            ymin = np.min(pk[min_idx:max_idx])
                            ymax = np.max(pk[min_idx:max_idx])
                            
                            if ymin < ylim[0] and (i,j) not in panel_exceptions:
                                ylim[0] = ymin
                            if ymax > ylim[1] and (i,j) not in panel_exceptions:
                                ylim[1] = ymax
                        
                        # after the loop, we have the new ylims for the panel. Set them
                        plt.ylim(ylim[0], ylim[1])
        

        return

    def defaultAxesLabels(self, dtype = 1, xpos = [], ypos = []):
        if dtype == 1:
            xlab = r'k (Mpc/h)$^{-1}$'
            ylab = r'P(k) (Mpc/h)$^{-3}$'
            
        elif dtype == 2:
            xlab = r"k$_{\parallel}$ (h/Mpc)"
            ylab = r"k$_{\perp}$ (h/Mpc)"
            
        elif dtype == 'slice':
            xlab = 'x (Mpc/h)'
            ylab = 'y (Mpc/h)'
        self.axisLabel(xlab, 'x', pos=xpos)
        self.axisLabel(ylab, 'y', pos=ypos)
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
                    if which == 'y' or which == 'both':
                        plt.ylim(ylim[0], ylim[1])
        
        return
            
    def saveFig(self, dir_path, rowp, colp, panelp, suffix = ''):
        outstr = '%sR_%sC_%s'%(rowp, colp, panelp)
        if not suffix == '':
            outstr += '_' + suffix 
        plt.savefig(dir_path + outstr + '.png')
        self.clf()
        return
