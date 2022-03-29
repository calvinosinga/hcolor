import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.gridspec as gspec
import copy
from hc_lib.plots.container import PostResult

class FigureLibrary():

    def __init__(self, rlib = None, result_type = 'pk'):
        if not rlib is None:
            self.results = rlib.results[result_type]
        else:
            self.results = []
        self.rt = result_type
        self.fig = None
        self.panels = None
        self.gsidx = None
        self.bigfont = 12
        self.smallfont = 10
        plt.rcParams["font.family"] = "serif"
        plt.rcParams["mathtext.fontset"] = 'dejavuserif'
        return
    
    ########## HANDLING FIGURE ORGANIZATION/CREATION #################################
    def getFig(self):
        if self.fig is None:
            raise ValueError("figure not made")
        return self.fig, self.panels
    
    
    def clf(self):
        plt.clf()
        plt.close()
        return

    def saveFig(self, dir_path, suffix = ''):
        outstr = '%sR_%sC_%s'%(self.rowprop, self.colprop, self.panelprop)
        if not suffix == '':
            outstr += '_' + suffix 
        self.fig.savefig(dir_path + outstr + '.pdf')
        self.clf()
        return
    
    def setGspecIndices(self, idxs):
        self.gsidx = idxs
        return

    def createFig(self, nrows, ncols, panel_length = 3, panel_bt = 0.1, 
                xborder = 1, yborder = 1, height_ratios = None,
                width_ratios = None):
        
        # border input can be either a list or single number
        if isinstance(xborder, float) or isinstance(xborder, int):
            xborder = [xborder, xborder]
        if isinstance(yborder, float) or isinstance(yborder, int):
            yborder = [yborder, yborder]
        if isinstance(panel_bt, float) or isinstance(panel_bt, int):
            panel_bt = [panel_bt, panel_bt]
        if height_ratios is None:
            height_ratios = np.ones(nrows) * panel_length
        else:
            # renormalize
            maxval = np.max(height_ratios)
            height_ratios /= maxval
            height_ratios *= panel_length

        if width_ratios is None:
            width_ratios = np.ones(ncols) * panel_length
        else:
            #renormalize
            maxval = np.max(width_ratios)
            width_ratios /= maxval
            width_ratios *= panel_length
        
        # creating Figure object

        figwidth = np.sum(width_ratios) + panel_bt[0] * (ncols - 1) + \
                xborder[0] + xborder[1]
        figheight = np.sum(height_ratios) + panel_bt[1] * (nrows - 1) + \
                yborder[0] + yborder[1]
        
        fig = plt.figure(figsize=(figwidth, figheight))

        self.fig = fig
        self.nrows = nrows
        self.ncols = ncols
        self.panel_length = panel_length
        self.panel_bt = panel_bt
        self.xborder = xborder
        self.yborder = yborder
        self.figsize = [figwidth, figheight]
        self.has_cbar_col = False

        return
    
    def createGrid(self, height_ratios = None, width_ratios= None):
        # needed fig params
        nrows = self.nrows
        ncols = self.ncols
        figheight = self.figsize[1]
        figwidth = self.figsize[0]
        yborder = self.yborder
        xborder = self.xborder
        panel_bt = self.panel_bt
        panel_length = self.panel_length

        if height_ratios is None:
            height_ratios = np.ones(nrows)*panel_length
        
        if width_ratios is None:
            width_ratios = np.ones(ncols)*panel_length
        # creating gridspec
        gs = gspec.GridSpec(nrows, ncols, left= xborder[0]/figwidth, right=1-xborder[1]/figwidth,
                top=1-yborder[1]/figheight, bottom=yborder[0]/figheight,
                wspace=panel_bt[0]*ncols/figwidth, hspace=panel_bt[1]*nrows/figheight,
                height_ratios = height_ratios, width_ratios = width_ratios)
        
        # making panels list
        panels = np.empty((nrows, ncols), dtype=object)
        for idx in self.gsidx:
            panels[idx] = self.fig.add_subplot(gs[idx])

        
        self.panels = panels
        return

    def createFigGrid(self, nrows, ncols, panel_length = 3, panel_bt = 0.1, 
                xborder = 1, yborder = 1, height_ratios = None, 
                width_ratios = None):

        # create Figure
        self.createFig(nrows, ncols, panel_length, panel_bt, 
                xborder, yborder, height_ratios, width_ratios)

        
        # set default gspec idxs if not already set
        if self.gsidx is None:
            gsidx = []
            for i in range(self.nrows):
                for j in range(self.ncols):
                    gsidx.append((i,j))
            self.setGspecIndices(gsidx)
        
        # create gspec
        self.createGrid(height_ratios, width_ratios)
        return
    
    def _isMatch(self, rc, desired_props):
        isMatch = True

        for k,v in desired_props.items():
            try:
                self_val = rc.props[k]
            except KeyError:
                self_val = 'no key'
            if self_val == 'no key':
                continue

            # if we don't have a list of desired values, check if the property
            # of the result has the the desired value. Auto powers only have one
            # property to check
            elif not isinstance(v, list) and not isinstance(self_val, list):
                isMatch = (isMatch and v == self_val)
            # if we do have a list of desired values, but the result is still an
            # auto power spectrum, check if self_val is in v
            elif isinstance(v, list) and not isinstance(self_val, list):
                isMatch = (isMatch and self_val in v)

            # if both are lists, we need to know if at least one value from self_val
            # is in the desired properties
            elif isinstance(v, list) and isinstance(self_val, list):
                one_val = False
                for i in range(len(self_val)):
                    if self_val[i] in v:
                        one_val = True
                isMatch = (isMatch and one_val)
            # the last case where v is not a list but self_val is
            elif not isinstance(v, list) and isinstance(self_val, list):
                isMatch = (isMatch and v in self_val)
            else:
                print('not all cases handled')
        return isMatch
    
    def getMatchingResults(self, iprops, rmprops, rcs = []):
        if not rcs:
            rcs = self.results
        matches = []
        for r in rcs:
            if self._isMatch(r, iprops):
                if not rmprops:
                    matches.append(r)
                elif not self._isMatch(r, rmprops):
                    matches.append(r)
        return matches
    
    def arrangeResults(self, iprops, rowp, rowvals,
            colp, colvals, panelp, rmprops = {}):
        figarr = np.empty((self.nrows, self.ncols), dtype = object)
        for i in range(self.nrows):
            for j in range(self.ncols):
                ip_temp = copy.copy(iprops)
                ip_temp[rowp] = rowvals[i]
                ip_temp[colp] = colvals[j]
                figarr[i,j] = self.getMatchingResults(ip_temp, rmprops)

        self.figarr = figarr
        self.rowprop = rowp
        self.colprop = colp
        self.panelprop = panelp
        return figarr
    
    def arrangeResultsReturn(self, iprops, rowp, rowvals,
            colp, colvals, rmprops = {}):
        figarr = np.empty((self.nrows, self.ncols), dtype = object)
        for i in range(self.nrows):
            for j in range(self.ncols):
                ip_temp = copy.copy(iprops)
                ip_temp[rowp] = rowvals[i]
                ip_temp[colp] = colvals[j]
                figarr[i,j] = self.getMatchingResults(ip_temp, rmprops)

        # self.figarr = figarr
        # self.rowprop = rowp
        # self.colprop = colp
        # self.panelprop = panelp
        return figarr
    
    def arrangePerPanel(self, iprops_per_panel, rmprops_per_panel, 
                    rowp = '', colp = '', panelp = ''):
        figarr = np.empty((self.nrows, self.ncols), dtype = object)
        self.rowprop = rowp
        self.colprop = colp
        self.panelprop = panelp
        for i in range(self.nrows):
            for j in range(self.ncols):
                idx = (i, j)
                iprops = iprops_per_panel[idx]
                rmprops = rmprops_per_panel[idx]
                figarr[i,j] = self.getMatchingResults(iprops, rmprops)
        self.figarr = figarr
        return figarr

    def setResultArray(self, figarr, rowp = '', colp = '', panelp = ''):
        self.figarr = figarr
        self.rowprop = rowp
        self.colprop = colp
        self.panelprop = panelp
        return                    

    def makeRatios(self, num_iprops, denom_iprops, num_rmprops = {},
                denom_rmprops = {}):
        nums = self.getMatchingResults(num_iprops, num_rmprops)
        denom = self.getMatchingResults(denom_iprops, denom_rmprops)
        ratios = []
        
        for r in nums:
            postr = PostResult()
            postr.computeRatio(r, denom)
            ratios.append(postr)
        
        self.results.extend(ratios)
        return
    
    def addObsBias(self, idx, nums, denom):
        ratios = []
        for r in nums:
            postr = PostResult()
            postr.computeBiasObs(r, denom)
            ratios.append(postr)
        if self.figarr[idx] is None:
            self.figarr[idx] = ratios
        else:
            self.figarr[idx].extend(ratios)
        return

    def makeObsBias(self, num_iprops, denom_iprops, num_rmprops = {}, 
                denom_rmprops = {}):
        nums = self.getMatchingResults(num_iprops, num_rmprops)
        denom = self.getMatchingResults(denom_iprops, denom_rmprops)
        ratios = []
        for r in nums:
            postr = PostResult()
            postr.computeBiasObs(r, denom)
            ratios.append(postr)
        
        self.results.extend(ratios)
        return
    
    def addColorRatios(self, idx, reds, blues):
        ratios = []
        for r in range(len(reds)):
            postr = PostResult()
            rprops = copy.copy(reds[r].props)
            rprops['color'] = 'blue'
            rprops['fieldname'] = rprops['fieldname'][0]
            del rprops['result_runtime']
            denom = self.getMatchingResults(rprops, {}, rcs = blues)
            postr.computeRatio(reds[r], denom[0])
            print(postr.props['space'])
            ratios.append(postr)
        if self.figarr[idx] is None:
            self.figarr[idx] = ratios
        else:
            self.figarr[idx].extend(ratios)
        return

    ################ DATA ACCESS/MANAGEMENT ############################################
    def addResults(self, rlib):
        results_from_other_rlib = rlib.results[self.rt]
        self.results.extend(results_from_other_rlib)
        return
    
    def setDim(self, nrows, ncols):
        self.nrows = nrows
        self.ncols = ncols
        return

    def getPropVals(self, propname, iprops = {}, rcs = []):
        if not rcs:
            rcs = self.results
        propvals = []
        for r in rcs:
            if iprops:
                is_match = self._isMatch(r, iprops)
            else:
                is_match = True
            if propname in r.props and is_match:
                rpval = r.props[propname]
                if rpval not in propvals:
                    propvals.append(rpval)
        return propvals
    
    def getDim(self):
        return [self.nrows, self.ncols]
    
    ################ INDIVIDUAL PANEL PLOTTING ROUTINES #############
    def plotLine(self, idx, iprops, rcs = [], line_kwargs = {}):
        if not rcs:
            rcs = self.figarr[idx]
        
        p = self.panels[idx[0]][idx[1]]

        for r in rcs:
            x, y, _ = r.getValues()

            if 'label' not in line_kwargs:
                line_kwargs['label'] = r.props[self.panelprop]
            if self._isMatch(r, iprops):

                p.plot(x, y, **line_kwargs)
        return

    def plotFill(self, idx, iprops, rcs = [], fill_kwargs = {}, dark_edges = False,
                line_kwargs = {}, ax = None):
        ys = []
        if not rcs:
            rcs = self.figarr[idx]

        for r in rcs:
            if self._isMatch(r, iprops):
                x, y, _ = r.getValues()
                ys.append(y)
        ys = np.array(ys)
        if ax is None:
            p = self.panels[idx[0]][idx[1]]
        else:
            p = ax
        mx = np.max(ys, axis=0)
        mn = np.min(ys, axis=0)

        if 'label' not in fill_kwargs:
            fill_kwargs['label'] = r.props[self.panelprop]
        if 'alpha' not in fill_kwargs:
            fill_kwargs['alpha'] = 0.3
        if 'color' not in fill_kwargs:
            fill_kwargs['color'] = 'blue'
        
        line_kwargs['visible'] = dark_edges
        line_kwargs['label'] = '_nolegend_'
        if 'color' not in line_kwargs:
            line_kwargs['color'] = fill_kwargs['color']
        
        p.plot(x,mn, **line_kwargs)
        p.plot(x,mx, **line_kwargs)
        p.fill_between(x, mn, mx, **fill_kwargs)
        return
    
    def plotMedian(self, idx, iprops, rcs = [], line_kwargs = {}, ax = None):
        ys = []
        if not rcs:
            rcs = self.figarr[idx]

        for r in rcs:
            if self._isMatch(r, iprops):
                x, y, _ = r.getValues()
                ys.append(y)
        ys = np.array(ys)
        if ax is None:
            p = self.panels[idx[0]][idx[1]]
        else:
            p = ax
#        mx = np.max(ys, axis=0)
#        mn = np.min(ys, axis=0)
        md = np.median(ys, axis = 0)
#        if 'label' not in fill_kwargs:
#            fill_kwargs['label'] = r.props[self.panelprop]
#        if 'alpha' not in fill_kwargs:
#            fill_kwargs['alpha'] = 0.55
#        if 'color' not in fill_kwargs:
#            fill_kwargs['color'] = 'blue'
        
#        line_kwargs['visible'] = dark_edges
#        line_kwargs['label'] = '_nolegend_'
#        if 'color' not in line_kwargs:
#            line_kwargs['color'] = fill_kwargs['color']
        
#        p.plot(x,mn, **line_kwargs)
#        p.plot(x,mx, **line_kwargs)
#        p.fill_between(x, mn, mx, **fill_kwargs)
            
        p.plot(x, md, **line_kwargs)
        return
    
    def plotSlice(self, idx, rc = None, im_kwargs = {}):
        if rc is None:
            rcs = self.figarr[idx]
            if len(rcs) > 1:
                raise ValueError("there is more than one result for this panel.")
            rc = rcs[0]
        
        cmap = self.cmap_arr[idx]
        norm = self.norm_arr[idx]

        xlim, ylim, data = rc.getValues()
        extent=(xlim[0], xlim[1], ylim[0], ylim[1])
                # x_bound, y_bound, mass = pslice.getValues()
                # extent=(x_bound[0], x_bound[1], y_bound[0], y_bound[1])
        mask = data < norm.vmin
        data[mask] = norm.vmin

        self.panels[idx[0]][idx[1]].imshow(data, cmap = cmap, norm = norm, aspect = 'auto', extent=extent, 
                origin='lower', **im_kwargs)
        return
    
    
    def plot2D(self, idx, rc = None, maxks = [5, 5], cstep = 0.5, ctr_kwargs = {},
                im_kwargs = {}):

        if rc is None:
            rcs = self.figarr[idx]
            if len(rcs) > 1:
                raise ValueError("there is more than one result for this panel.")
            rc = rcs[0]

        kpar, kper, pk = rc.getValues()
        p = self.panels[idx[0]][idx[1]]
        cmap = self.cmap_arr[idx]
        norm = self.norm_arr[idx]
        kpar = np.unique(kpar)
        kper = np.unique(kper)
        paridx = np.where(kpar>maxks[0])[0][0]
        peridx = np.where(kper>maxks[1])[0][0]

        pk = np.reshape(pk, (len(kper), len(kpar)))
        plotpk = np.log10(pk[:paridx, :peridx])
        KPAR, KPER = np.meshgrid(kpar[:peridx], kpar[:paridx])
        levels = np.arange(int(norm.vmin), int(norm.vmax)+1, cstep)
        if 'color' not in ctr_kwargs:
            ctr_kwargs['color'] = 'black'
        
        if 'linestyles' not in ctr_kwargs:
            ctr_kwargs['linestyles'] = 'solid'
        p.contour(KPAR, KPER, plotpk, vmin=norm.vmin,
                vmax=norm.vmax, levels = levels,
                **ctr_kwargs)
        extent = (np.min(KPAR),np.max(KPAR),np.min(KPER),np.max(KPER))
                
        p.imshow(plotpk, extent=extent, origin='lower', aspect = 'auto',
                    norm=norm, cmap=cmap, **im_kwargs)
        return
    
    def _defaultNorms(self):
        if self.rt == '2Dpk':
            vlim_list = [[-2, 4] for i in range(self.nrows)]
            norm_arr = np.empty((self.nrows, self.ncols), dtype = object)
            for i in range(self.nrows):
                for j in range(self.ncols):
                    vlim = vlim_list[i]
                    norm_arr[i,j] = mpl.colors.Normalize(vmin=vlim[0], vmax=vlim[1])

        elif self.rt == 'slice':
            vlim_list = [[2, 12.5] for i in range(self.nrows)]
            norm_arr = np.empty((self.nrows, self.ncols), dtype = object)
            for i in range(self.nrows):
                for j in range(self.ncols):
                    vlim = vlim_list[i]
                    norm_arr[i,j] = mpl.colors.Normalize(vmin=vlim[0], vmax=vlim[1])
        
        else:
            raise NotImplementedError("default Norm not defined for result type %s"%self.rt)
        return norm_arr

    def assignNorms(self, norm_arr = None):
        if norm_arr is None:
            self.norm_arr = self._defaultNorms()
        else:
            self.norm_arr = norm_arr
        self.has_cbar_col = True
        return
    
    def _defaultCmaps(self):
        cmap_name = 'plasma'
        txt_kwargs = copy.copy(txt_kwargs)
        under = 'w'
        over = None
        cmap_arr = np.empty((self.nrows, self.ncols), dtype=object)
        cmap = copy.copy(mpl.cm.get_cmap(cmap_name))
        if not under is None:
            cmap.set_under(under)
        if not over is None:
            cmap.set_over(over)
        
        cmap_arr[:,:] = cmap
        return cmap_arr

    def assignCmaps(self, cmap_arr = None):
        if cmap_arr is None:
            self.cmap_arr = self._defaultCmaps()
        else:
            self.cmap_arr = cmap_arr
        self.has_cbar_col = True
        return
    
    def makeCbar(self, idx, label = '', label_kwargs = {}):
        p = self.panels[idx[0]][idx[1]]
        norm = self.norm_arr[idx]
        cmap = self.cmap_arr[idx]
        cbar = self.fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), cax=p)
        p.set_aspect(12, anchor = 'W')
        cbar.set_label(label, **label_kwargs)
        self.has_cbar_col = True
        return

    ########### HANDLING LABELS #########################################################
    def rowLabels(self, rowlabels, colidx = 0, pos = (0.05, 0.05), txt_kwargs = {}):
        if 'va' not in txt_kwargs:
            txt_kwargs['va'] = 'bottom'
        
        if 'ha' not in txt_kwargs:
            txt_kwargs['ha'] = 'left'
        
        if 'fontsize' not in txt_kwargs:
            txt_kwargs['fontsize'] = self.smallfont
        
        for i in range(self.nrows):
            p = self.panels[i][colidx]

            p.text(pos[0], pos[1], rowlabels[i], 
                        transform = p.transAxes, **txt_kwargs)
        
        return
    

    def colLabels(self, collabels, row_idx = 0, in_panel = True, pos = (0.5, 0.95),
                txt_kwargs = {}):
        ncols = self.ncols

        if 'fontsize' not in txt_kwargs:
            txt_kwargs['fontsize'] = self.smallfont
        
        if 'va' not in txt_kwargs:
            txt_kwargs['va'] = 'top'
        
        if 'ha' not in txt_kwargs:
            txt_kwargs['ha'] = 'center'
        
        if in_panel:
            for j in range(ncols):
                p = self.panels[row_idx][j]
                p.text(pos[0], pos[1], collabels[j], transform = p.transAxes,
                        **txt_kwargs)
        else:

            for j in range(ncols):
                p = self.panels[row_idx][j]
            
                p.xaxis.set_label_position('top')
                p.set_xlabel(collabels[j], **txt_kwargs)
        return

    def _defaultAxesLabels(self, axis, subscript = ''):
        if self.rt == 'pk':
            xlab = "k (Mpc/h)$^{-1}$"
            ylab = "P$_{" + subscript + "}$ (k) (Mpc/h)$^{-3}$"
            
        elif self.rt == '2Dpk':
            xlab = "k$_{\\parallel}$ (Mpc/h)$^{-1}$"
            ylab = "k$_{\\perp}$ (Mpc/h)$^{-1}$"
            clab = 'log P$_{'+subscript+'}$ (k$_{\\parallel}$, k$_{\\perp}$) (Mpc/h)$^{-3}$'
            
        elif self.rt == 'slice':
            xlab = 'x (Mpc/h)'
            ylab = '' # understood to also be position
            clab = 'log M$_{'+subscript+'}$ / M$_{\\odot}$'

        else:
            raise NotImplementedError("result type %s does not have a default axis label"%self.rt)
        if axis == 'x':
            return xlab
        elif axis == 'y':
            return ylab
        elif axis == 'c':
            return clab
        else:
            raise ValueError("invalid axis %s given"%axis)
        
        
    def axisLabel(self, axis, text = '', subscript = '',
                pos = [], txt_kwargs = {}):
        posdict = {}
        txt_kwargs = copy.copy(txt_kwargs)
        if axis == 'x':
            if 'rotation' not in txt_kwargs:
                txt_kwargs['rotation'] = 'horizontal'
            if self.has_cbar_col:
                ncols = self.ncols - 1 # does not include cbar panel
                image_length = ncols * self.panel_length + \
                        self.panel_bt[0] * (ncols - 1)
                
                hpos = (0.5 * image_length + self.xborder[0]) / self.figsize[0]
            else:
                hpos = 0.5
            posdict['x'] = [hpos, self.yborder[1]/3/self.figsize[1]]
        elif axis == 'y':
            if 'rotation' not in txt_kwargs:
                txt_kwargs['rotation'] = 'vertical'
            
            posdict['y'] = [self.xborder[0]/3/self.figsize[0], 0.5]
        
        if text == '':
            text = self._defaultAxesLabels(axis, subscript)
        
        if not pos:
            pos = posdict[axis]
        
        if 'fontsize' not in txt_kwargs:
            txt_kwargs['fontsize'] = self.bigfont
        if 'ha' not in txt_kwargs:
            txt_kwargs['ha'] = 'center'
        if 'va' not in txt_kwargs:
            txt_kwargs['va'] = 'center'
        self.fig.text(pos[0], pos[1], text, **txt_kwargs)
        del txt_kwargs
        return
    
    def labelPanelAxis(self, idx, which, text, txt_kwargs):
        ax = self.panels[idx]
        if which == 'x':
            ax.set_xlabel(text, **txt_kwargs)
        if which == 'y':
            ax.set_ylabel(text, **txt_kwargs)
        return

    def addLegend(self, idx = (0,0), kwargs = {}):
        p = self.panels[idx[0]][idx[1]]
        if 'fontsize' not in kwargs:
            kwargs['fontsize'] = self.smallfont
        
        if 'frameon' not in kwargs:
            kwargs['frameon'] = False
        
        if 'loc' not in kwargs:
            kwargs['loc'] = 'upper right'
        p.legend(**kwargs)
        return
     
    ########## HANDLING TICKS #################################################
    def removeYTickLabels(self, panel_exceptions = []):
        if not panel_exceptions:
            panel_exceptions = self._defaultTickLabelPanelExceptions('y')
        self._removeTickLabels('y', panel_exceptions)
        return
    
    def _defaultTickLabelPanelExceptions(self, axis):
        if axis == 'y':
            return [(i, 0) for i in range(self.nrows)]
        elif axis == 'x':
            return [(self.nrows-1, i) for i in range(self.ncols)]
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
    
    def changeTickParams(self, kwargs = {}, panel_exceptions=[]):
        if not 'direction' in kwargs:
            kwargs['direction'] = 'in'
        
        if not 'which' in kwargs:
            kwargs['which'] = 'both'

        if not 'labelsize' in kwargs:
            kwargs['labelsize'] = self.smallfont

        for i in range(self.nrows):
            for j in range(self.ncols):
                if (i,j) not in panel_exceptions:
                    self.panels[i][j].tick_params(axis='both', **kwargs)
        return

    def _removeTickLabels(self, axis, panel_exceptions = []):
        
        for i in range(self.nrows):
            for j in range(self.ncols):
                if (i, j) not in panel_exceptions:
                    p = self.panels[i][j]
                    if axis == 'y':
                        p.yaxis.set_ticklabels([])
                    elif axis == 'x':
                        p.xaxis.set_ticklabels([])
        return
    
    ############### HANDLING AXES ########################################3
    def _getLimits(self, panel_exceptions = []):
        ylims = np.zeros((self.nrows, self.ncols, 2))
        xlims = np.zeros_like(ylims)
        for i in range(self.nrows):
            for j in range(self.ncols):
                p = self.panels[i][j]
                ymin, ymax = p.get_ylim()
                xmin, xmax = p.get_xlim()

                if (i, j) in panel_exceptions:
                    ylims[i,j,:] = np.nan
                    xlims[i,j,:] = np.nan
                else:
                    ylims[i,j,0], ylims[i,j,1] = ymin, ymax
                    xlims[i,j,0], xlims[i,j,1] = xmin, xmax
        return xlims, ylims

    def xLimAdjustToNyquist(self, shift = 0.0, panel_exceptions = []):
        
        for i in range(self.nrows):
            for j in range(self.ncols):
                if (i, j) not in panel_exceptions:
                    p = self.panels[i][j]
                    
                    res_container_list = self.figarr[i, j]
                    xmin, xmax = p.get_xlim()
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
                        p.set_xlim(mink, nyq - shift)
                    
                    else:
                        p.set_xlim(xmin, nyq - shift)
        self.matchAxisLimits(which='x', panel_exceptions=panel_exceptions)
        return
    
    def flushYAxisToData(self, result_type = 'pk', panel_exceptions = []):
        
        for i in range(self.nrows):
            for j in range(self.ncols):
                if (i, j) not in panel_exceptions:
                    p = self.panels[i][j]
                    lines = p.get_lines()
                    xmin, xmax = p.get_xlim()
                    ylim = [np.inf, -np.inf] # each panel is flushed individually, reset ylim vals
                    if result_type == 'pk':
                        for l in lines:
                            wavenum, pk = l.get_data()

                            max_idx = np.argmax(wavenum > xmax)
                            min_idx = np.argmax(wavenum < xmin)
                            ymin = np.min(pk[min_idx:max_idx])
                            ymax = np.max(pk[min_idx:max_idx])
                            
                            if ymin < ylim[0] and (i,j) not in panel_exceptions:
                                ylim[0] = ymin
                            if ymax > ylim[1] and (i,j) not in panel_exceptions:
                                ylim[1] = ymax
                        
                        # after the loop, we have the new ylims for the panel. Set them
                        p.set_ylim(ylim[0], ylim[1])
        

        return
    
    def matchAxisLimits(self, which = 'both', panel_exceptions = [], match_line = True):
        xlims, ylims = self._getLimits(panel_exceptions)
        
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
            
        for i in range(self.nrows):
            for j in range(self.ncols):
                if (i,j) not in panel_exceptions:
                    p = self.panels[i][j]
                    if which == 'both' or which == 'x':
                        p.set_xlim(xlims[i,j,0], xlims[i,j,1])
                    if which == 'both' or which == 'y':
                        p.set_ylim(ylims[i,j,0], ylims[i,j,1])
        return
    
    def logAxis(self, which = 'both', panel_exceptions = []):
        
        for i in range(self.nrows):
            for j in range(self.ncols):
                if (i, j) not in panel_exceptions:
                    p = self.panels[i][j]

                    if which == 'both' or which == 'x':
                        p.set_xscale('log')
                    if which == 'both' or which == 'y':
                        p.set_yscale('log')
        return
