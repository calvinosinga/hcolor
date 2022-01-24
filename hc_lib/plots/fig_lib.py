import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.gridspec as gspec
import copy
import illustris_python as il
import h5py as hp
mpl.rcParams['text.usetex'] = True
# mpl.rcParams['figure.max_open_warning'] 
tng_dict = {'tng100':'L75n1820TNG', 'tng300':'L205n2500TNG',
        'tng100-2':'L75n910TNG', 'tng100-3':'L75n455TNG', 
        'tng50':'L35n2160TNG'}
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
        plt.close()
        return
    
    def plotLines(self, panel_prop, labels = None, colors = None, linestyles = None):
        dim = self.dim
        default_color_cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
        pprop = panel_prop

        def _plot_auto(r_container, idx):
            """
            Plots a panel when the results to be plotted (rc_panel)
            is a list of ResultContainer objects. This is default.
            """
            
            x, y, z = r_container.getValues()
                 
            if labels is None:
                l_lab = r_container.props[pprop]
            elif not r_container.props[pprop] in labels:
                l_lab = r_container.props[pprop]
            else:
                l_lab = labels[r_container.props[pprop]]

            if colors is None:
                l_c = default_color_cycle[idx%len(default_color_cycle)]
            elif not r_container.props[pprop] in colors:
                l_c = default_color_cycle[idx%len(default_color_cycle)]
            else:
                l_c = colors[r_container.props[pprop]]

            if linestyles is None:    
                l_ls = '-'
            elif not r_container.props[pprop] in linestyles:
                l_ls = '-'
            else:
                l_ls = linestyles[r_container.props[pprop]]
            
            plt.plot(x, y, label = self.texStr(l_lab), color = l_c, 
                    linestyle = l_ls)
            
            return

        def _plot_cross(r_container, idx):
            x,y,z = r_container.getValues()
            ppropval = r_container.props[pprop]
            def _find_line_property(gdict, def_val):
                if gdict is None:
                    return def_val
                elif isinstance(ppropval, list):
                    if ppropval[0] in gdict:
                        return gdict[ppropval[0]]
                    elif ppropval[1] in gdict:
                        return gdict[ppropval[1]]
                    else:
                        return def_val
                else:
                    if ppropval in gdict:
                        return gdict[ppropval]
                    else:
                        return def_val

            l_lab = _find_line_property(labels, ppropval)
            l_c = _find_line_property(colors, 
                    default_color_cycle[idx%len(default_color_cycle)])
            l_ls = _find_line_property(linestyles, '-')
            
            
            plt.plot(x, y, label = self.texStr(l_lab), color = l_c, 
                    linestyle = l_ls)
            return
        
        for i in range(dim[0]):
            for j in range(dim[1]):
                p = self.panels[i][j]

                results_for_panel = self.figArr[i, j]
                plt.sca(p)
                for r in range(len(results_for_panel)):
                    rc = results_for_panel[r]
                    if rc.props['is_auto']:
                        _plot_auto(rc,r)
                    else:
                        _plot_cross(rc,r)

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

    def plotSlices(self, plot_scatter = True):
        #print(self.dim)
        #print(len(self.panels), len(self.panels[0]))
        for i in range(self.dim[0]):
            for j in range(self.dim[1]):
                #print(i,j)
                p = self.panels[i][j]

                if len(self.figArr[i, j]) > 1:
                    print('needs only one slice: panel %d,%d'%(i,j))
                    for r in self.figArr[i, j]:
                        print(r.props)
                pslice = self.figArr[i, j][0]

                plt.sca(p)
                xlim, ylim, mass = pslice.getValues()
                cmap = self.cmap_arr[i, j]
                norm = self.norm_arr[i, j]

                # if plot_scatter and pslice.getProp('is_groupcat'):
                    # xpos = np.linspace(xlim[0], xlim[1], mass.shape[0])
                    # ypos = np.linspace(ylim[0], ylim[1], mass.shape[1])
                    # galxpos = np.zeros(mass.shape[0] + mass.shape[1])
                    # galypos = np.zeros_like(galxpos)
                    # sizes = np.zeros_like(galxpos)
                    # colors = np.zeros((galxpos.shape[0], 4))
                    # sm = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
                    # for n in range(mass.shape[0]):
                    #     for m in range(mass.shape[1]):
                    #         if mass[n, m] > norm.vmin:
                    #             galxpos[n+m] = xpos[n]
                    #             galypos[n+m] = ypos[m]
                    #             sizes[n+m] = mass[n, m]
                    #             colors[n+m, :] = sm.to_rgba(mass[n, m])
                    
                    # sizes = sizes/np.max(sizes) * 5
                    # plt.scatter(galxpos, galypos, s=sizes, c=colors)
                    
                    # TEMPORARY SLICE PLOT
                if plot_scatter and pslice.getProp('fieldname') == 'galaxy':
                    f = il.groupcat.loadSubhalos('/lustre/cosinga/L75n1820TNG/output/', 99, fields=['SubhaloPos', 'SubhaloMassType', 'SubhaloVel'])
                    mid = pslice.props['box']/2
                    mnm = mid - pslice.props['box'] * 0.1
                    mxm = mid + pslice.props['box'] * 0.1
                    pos = f['SubhaloPos'][:]/1e3
                    mass = f['SubhaloMassType'][:]*1e10/.6774
                    pos_mask = (pos[:,1]> mnm) & (pos[:,1]<mxm)
                    mass_mask = (mass[:,4] > 200*1.4e6)
                    mask = pos_mask & mass_mask
                    x = pos[mask, 2]
                    y = pos[mask, 0]
                    
                    sizes = np.log10(np.sum(mass[mask, :], axis=1))
                    colors = np.zeros((sizes.shape[0], 4))
                    sm = mpl.cm.ScalarMappable(norm = norm, cmap = cmap)
                    for s in range(len(sizes)):
                        colors[s, :] = sm.to_rgba(sizes[s])
                    sizes = sizes/np.max(sizes) * 5
                    print(x.shape)
                    plt.scatter(x,y, s=sizes, c=colors)
                elif plot_scatter and pslice.getProp('fieldname') == 'hisubhalo':
                    f = il.groupcat.loadSubhalos('/lustre/cosinga/L75n1820TNG/output/', 99, fields=['SubhaloPos','SubhaloVel'])
                    h = hp.File('/lustre/cosinga/L75n1820TNG/postprocessing/hih2/hih2_galaxy_099.hdf5', 'r')
                    ids = h['id_subhalo'][:]
                    ids = ids.astype(np.int32)
                    pos = f['SubhaloPos'][ids]
                    vel = f['SubhaloVel'][ids]
                    
                    mid = pslice.props['box']/2
                    mnm = mid - pslice.props['box'] * 0.1
                    mxm = mid + pslice.props['box'] * 0.1                    
                    pos_mask = (pos[:,1]> mnm) & (pos[:,1]<mxm)
                    x = pos[pos_mask, 2]
                    y = pos[pos_mask, 0]
                    
                    mass = h[pslice.props['model']][pos_mask]
                    sizes = np.log10(mass)
                    colors = np.zeros((sizes.shape[0], 4))
                    sm = mpl.cm.ScalarMappable(norm = norm, cmap = cmap)
                    for s in range(len(sizes)):
                        colors[s,:] = sm.to_rgba(sizes[s])
                    sizes = sizes/np.max(sizes) * 5
                    print(x.shape)
                    plt.scatter(s,y,s=sizes,c=colors)
                else:
                    extent=(xlim[0], xlim[1], ylim[0], ylim[1])
                # x_bound, y_bound, mass = pslice.getValues()
                # extent=(x_bound[0], x_bound[1], y_bound[0], y_bound[1])
                
                    plt.imshow(mass, cmap = cmap, norm = norm, aspect = 'auto', extent=extent, 
                            origin='lower')
            
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
                    plt.plot(xbins, 0.65 + 0.02 * (xbins - 10.28), color='gray', linestyle = '--')
        
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
            vlim_list = [[2, 12.5] for i in range(self.dim[0])]
        norm_arr = np.empty_like(self.figArr, dtype = object)
        for i in range(self.dim[0]):
            for j in range(self.dim[1]):
                vlim = vlim_list[i]
                norm_arr[i,j] = mpl.colors.Normalize(vmin=vlim[0], vmax=vlim[1])
        self.norm_arr = norm_arr
        return
    
    def assignHistNorms(self, vlim_list = []):
        if not vlim_list:
            vlim_list = [[1, 5e2] for i in range(self.dim[0])]
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
                        if r.props['is_auto']:    
                            nyq_temp = r.props['grid_resolution'] * np.pi / r.props['box']
                        else:
                            nyq_temp = r.props['grid_resolution'][0] * np.pi / r.props['box'][0]
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
            # ylab = 'y (Mpc/h)'
            ylab = '' # understood to also be position
        self.axisLabel(xlab, 'x', pos=xpos)
        self.axisLabel(ylab, 'y', pos=ypos)
        return

    
    def _getLimits(self, panel_exceptions = []):
        dim = self.dim
        ylims = np.zeros((dim[0], dim[1], 2))
        xlims = np.zeros_like(ylims)
        for i in range(dim[0]):
            for j in range(dim[1]):
                p = self.panels[i][j]
                plt.sca(p)
                ymin, ymax = plt.ylim()
                xmin, xmax = plt.xlim()
                # if not (i, j) in panel_exceptions:
                #     # for the y-axis, we want the largest max, smallest min
                #     # in order to encompass the most data
                #     if ymin < ylims[0]:
                #         ylims[0] = ymin
                #     if ymax > ylims[1]:
                #         ylims[1] = ymax
                #     # for the x-axis, we want the smallest max, largest min
                #     # so no panel includes bad data
                #     if xmin > xlims[0]:
                #         xlims[0] = xmin
                #     if xmax < xlims[1]:
                #         xlims[1] = xmax
                # else:
                if (i, j) in panel_exceptions:
                    ylims[i,j,:] = np.nan
                    xlims[i,j,:] = np.nan
                else:
                    ylims[i,j,0], ylims[i,j,1] = ymin, ymax
                    xlims[i,j,0], xlims[i,j,1] = xmin, xmax
        
        return xlims, ylims
    
    def matchAxisLimits(self, which = 'both', panel_exceptions = [], match_line = True):
        xlims, ylims = self._getLimits(panel_exceptions)
        dim = self.dim
        
        new_xlims = np.ma.masked_invalid(xlims)
        new_ylims = np.ma.masked_invalid(ylims)
        if not match_line:
            # match every panel
            max_xlim = np.max(new_xlims)
            min_xlim = np.min(new_xlims)
            max_ylim = np.max(new_ylims)
            min_ylim = np.max(new_ylims)

            xlims[:,:,0] = min_xlim
            xlims[:,:,1] = max_xlim
            ylims[:,:,0] = min_ylim
            ylims[:,:,1] = max_ylim
        
        else:
            # match the limits of the respective row or column
            max_xlims = np.max(new_xlims[:,:,1], axis=0)
            min_xlims = np.min(new_xlims[:,:,0], axis=0)

            max_ylims = np.max(new_ylims[:,:,1], axis=1)
            min_ylims = np.min(new_ylims[:,:,0], axis=1)

            for i in range(len(max_xlims)):
                xlims[:,i,0]=min_xlims[i]
                xlims[:,i,1]=max_xlims[i]
            for i in range(len(max_ylims)):
                ylims[i,:,0]=min_ylims[i]
                ylims[i,:,1] = max_ylims[i]
            
        for i in range(dim[0]):
            for j in range(dim[1]):
                if (i,j) not in panel_exceptions:
                    plt.sca(self.panels[i][j])
                    if which == 'both' or which == 'x':
                        plt.xlim(xlims[i,j,0], xlims[i,j,1])
                    if which == 'both' or which == 'y':
                        plt.ylim(ylims[i,j,0], ylims[i,j,1])



        
        return
            
    def saveFig(self, dir_path, rowp, colp, panelp, suffix = ''):
        outstr = '%sR_%sC_%s'%(rowp, colp, panelp)
        if not suffix == '':
            outstr += '_' + suffix 
        plt.savefig(dir_path + outstr + '.png')
        self.clf()
        return
