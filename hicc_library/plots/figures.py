from hicc_library.plots import plot_lib as plib
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.gridspec as gspec
import copy
import numpy as np
mpl.rcParams['text.usetex'] = True

class Figs():

    def __init__(self):        
        self.results = []
        return

    def addResult(self, result):
        in_results = False
        for r in self.results:
            if r.equals(result):
                in_results = True
        if not in_results:
            self.results.append(result)
        else:
            raise ValueError("result is already in Figs object")
        return
    
    def removeResult(self, result):
        found = False
        for r in range(len(self.results)):
            if self.results[r].equals(result):
                del self.results[r]
                found = True
        if not found:
            print("did not find result that was supposed to be removed")
        return
            
    
    def _fetchResults(self, fieldname, snapshot = -1):
        field_results = []
        for r in self.results:
            if r.fieldname == fieldname:
                if snapshot == -1:
                    field_results.append(r)
                elif r.snapshot == snapshot:
                    field_results.append(r)
                    
        return field_results
        
    def _fetchKeys(self, substrings, keylist):
        res = []
        for sub in substrings:
            for k in keylist:
                if sub in k and not k in res:
                    res.append(k)
        
        if 'k' in res:
            res.remove('k')
        return res

    def _rmKeys(self, keywords, keylist):
        klist = copy.copy(keylist)
        for word in keywords:
            for k in klist:
                if word in k:
                    klist.remove(k)
        klist.remove('k')
        return klist

    def HI_auto_pk(self, in_rss = False, panel_length = 3, panel_bt = 0.1, text_space=0.1):
        """
        Makes HI-auto power spectra plots, for real space or redshift space.
        Each panel represents another redshift.

        hiptls: list of hiptl objects
        hisubs: list of hisubhalo objects
        vns: list of vn objects
        """
        # get the fields that are needed for this result:
        hiptls = self._fetchResults('hiptl')
        hisubs = self._fetchResults('hisubhalo')
        vns = self._fetchResults('vn')

        # get the desired keys for each field
        if in_rss:
            vnkeys = ['vn']
            hiptlkeys = self._rmKeys(['rs'], list(hiptls[0].pks.keys()))
            hisubkeys = self._rmKeys(['rs'], list(hisubs[0].pks.keys()))
        else:
            vnkeys = ['vnrs']
            hiptlkeys = self._fetchKeys(['rs'], list(hiptls[0].pks.keys()))
            hisubkeys = self._fetchKeys(['rs'], list(hisubs[0].pks.keys()))        
        # get the yrange
        yrange = [np.inf, 0]
        fields = []
        fields.extend(hiptls)
        fields.extend(hisubs)
        fields.extend(vns)

        for f in fields:
            if f.fieldname == 'hiptl':
                keys = hiptlkeys
            if f.fieldname == 'hisubhalo':
                keys = hisubkeys
            if f.fieldname == 'vn':
                keys = vnkeys

            for k in keys:
                pkmax = np.max(f.pks[k])
                pkmin = np.min(f.pks[k])
                if pkmax > yrange[1]:
                    yrange[1] = pkmax
                if pkmin < yrange[0]:
                    yrange[0] = pkmin
        del fields

        # get info from the fields to prepare plot
        box = hiptls[0].header['BoxSize']
        snapshots = []
        for f in hiptls:
            if not f.snapshot in snapshots:
                snapshots.append(f.snapshot)
        
        # put snapshots in increasing order
        snapshots.sort()
        
        # creating figure
        npanels = len(snapshots)
        figwidth = panel_length * npanels + panel_bt * (npanels - 1)
        figheight = panel_length
        fig = plt.figure(figsize = (figwidth, figheight))

        # creating gridspec
        gs = gspec.GridSpec(1, npanels)
        plt.subplots_adjust(left = panel_bt / figwidth,
                right = 1 - panel_bt / figwidth, top = 1 - panel_bt / figwidth,
                bottom = panel_bt/figwidth, wspace = panel_bt, hspace = panel_bt)

        # now creating panels in order of increasing redshift
        panels = []
        for i in range(npanels):
            panels.append(fig.add_subplot(gs[i]))

        # now making each panel
        for i in range(npanels):
            plt.sca(panels[i])
            panel_snap = snapshots[i]

            # plot the VN18 that matches the panel's redshift
            for pf in vns:
                if pf.snapshot == panel_snap:
                    plib.plotpks(pf.pks['k'], pf.pks, box, pf.axis, pf.resolution,
                            keylist = vnkeys, colors = ['green'],
                            labels = ['V-N18'])
            
            # plot the D18-Subhalo that matches the panel's redshift
            for pf in hisubs:
                if pf.snapshot == panel_snap:
                    plib.fillpks(pf.pks['k'], pf.pks, box, pf.axis, pf.resolution,
                            keylist = hisubkeys, color = 'orange',
                            label = 'D18-Subhalo')
            
            # plot the D18-Particle that matches the panel's redshift
            for pf in hisubs:
                if pf.snapshot == panel_snap:
                    plib.fillpks(pf.pks['k'], pf.pks, box, pf.axis, pf.resolution,
                            keylist = hiptlkeys, color = 'blue',
                            label = 'D18-Particle')

                
            # cosmetic tasks
            if not i == 0:
                ax = plt.gca()
                ax.set_yticklabels([])
                plt.ylabel('')
                ax.get_legend().remove()
            else:
                plt.legend(loc = 'upper right')
            plt.ylim(yrange[0], yrange[1])
            
            # output textbox onto the plot with redshift
            plt.text(hiptls[0].pks['k'] + text_space, yrange[0] + text_space,
                    'z=%.1f'%snapshots[i], fontsize = 20, ha = 'left', va = 'bottom',
                    fontweight = 'bold') 

        return

    def HI_auto_redshift_vs_real(self, panel_length = 3, panel_bt = 0.1, text_space=0.1):
        """
        Makes HI auto power spectra plots, but separates them by methodology to compare
        redshift-space and real-space plots.
        """
        # get the needed results
        hiptls = self._fetchResults('hiptl')
        hisubs = self._fetchResults('hisubhalo')
        vns = self._fetchResults('vn')

        # get the desired keys for each field
        vnkeys = ['vn']
        hiptlkeys = self._rmKeys(['rs'], list(hiptls[0].pks.keys()))
        hisubkeys = self._rmKeys(['rs'], list(hisubs[0].pks.keys()))
        
        vnrskeys = ['vnrs']
        hiptlrskeys = self._fetchKeys(['rs'], list(hiptls[0].pks.keys()))
        hisubrskeys = self._fetchKeys(['rs'], list(hisubs[0].pks.keys()))        
        # get the yrange
        yrange = [np.inf, 0]
        fields = []
        fields.extend(hiptls)
        fields.extend(hisubs)
        fields.extend(vns)

        for f in fields:
            if f.fieldname == 'hiptl':
                keys = hiptlkeys
            if f.fieldname == 'hisubhalo':
                keys = hisubkeys
            if f.fieldname == 'vn':
                keys = vnkeys

            for k in keys:
                pkmax = np.max(f.pks[k])
                pkmin = np.min(f.pks[k])
                if pkmax > yrange[1]:
                    yrange[1] = pkmax
                if pkmin < yrange[0]:
                    yrange[0] = pkmin
        del fields

        # get info from the fields to prepare plot
        box = hiptls[0].header['BoxSize']
        snapshots = []
        for f in hiptls:
            if not f.snapshot in snapshots:
                snapshots.append(f.snapshot)
        
        # put snapshots in increasing order
        snapshots.sort()
        
        # creating figure
        nrows = len(snapshots)
        ncols = 3 # for each methodology
        figwidth = panel_length * ncols + panel_bt * (ncols - 1)
        figheight = panel_length * nrows + panel_bt * (nrows - 1)
        fig = plt.figure(figsize = (figwidth, figheight))

        # creating gridspec
        gs = gspec.GridSpec(nrows, ncols)
        plt.subplots_adjust(left = panel_bt / figwidth,
                right = 1 - panel_bt / figwidth, top = 1 - panel_bt / figwidth,
                bottom = panel_bt/figwidth, wspace = panel_bt, hspace = panel_bt)

        # now creating panels in order of increasing redshift
        panels = []
        for i in range(nrows):
            col_panels = []
            for j in range(ncols):
                col_panels.append(fig.add_subplot(gs[i,j]))
            panels.append(fig.add_subplot(gs[i]))
        
        for i in range(nrows):
            # make the hisubhalo plot for this redshift
            plt.sca(panels[i][0])
            plib.fillpks(hisubs[i].pks['k'], hisubs[i].pks, box, hisubs[i].resolution,
                    keylist = hisubkeys, color = 'blue', label = 'real-space')

            plib.fillpks(hisubs[i].pks['k'], hisubs[i].pks, box, hisubs[i].resolution,
                    keylist = hisubrskeys, color = 'red', label = 'redshift-space')
            plt.ylim(yrange[0], yrange[1])
            
            # cosmetic tasks
            plt.text(hisubs[i].pks['k'][0]+text_space, yrange[0] + text_space, 'z=%.1f'%snapshots[i],
                    fontsize = 20, ha = 'left', va = 'bottom', fontweight = 'bold')


            ax = plt.gca()
            plt.ylabel('')
            if i == 0:
                ax.xaxis.set_label_position('top')
                plt.xlabel('D18-Subhalo', fontsize=16)
                plt.legend(loc = 'upper right')
            else:
                plt.xlabel('')
                ax.get_legend().remove()

            # make the hiptl plot
            plt.sca(panels[i][1])
            plib.fillpks(hiptls[i].pks['k'], hiptls[i].pks, box, hiptls[i].resolution,
                    keylist = hiptlkeys, color = 'blue', label = 'real-space')

            plib.fillpks(hiptls[i].pks['k'], hiptls[i].pks, box, hiptls[i].resolution,
                    keylist = hiptlrskeys, color = 'red', label = 'redshift-space')
            plt.ylim(yrange[0], yrange[1])
            
            # cosmetic tasks
            ax = plt.gca()
            plt.ylabel('')
            ax.set_yticklabels([])
            ax.get_legend().remove()
            if i == 0:
                ax.xaxis.set_label_position('top')
                plt.xlabel('D18-Particle', fontsize=16)
                plt.legend(loc = 'upper right')
            else:
                plt.xlabel('')
            # make the vn plot
            plt.sca(panels[i][2])
            plib.plotpks(vns[i].pks['k'], vns[i].pks, box, vns[i].resolution,
                    keylist = vnkeys, colors = ['blue'], labels = ['real-space'])

            plib.plotpks(vns[i].pks['k'], vns[i].pks, box, vns[i].resolution,
                    keylist = vnrskeys, colors = ['red'], labels = ['redshift-space'])
            plt.ylim(yrange[0], yrange[1])

            # cosmetic tasks
            ax = plt.gca()
            plt.ylabel('')
            ax.set_yticklabels([])
            ax.get_legend().remove()
            if i == 0:
                ax.xaxis.set_label_position('top')
                plt.xlabel('VN18', fontsize=16)
                plt.legend(loc = 'upper right')
            else:
                plt.xlabel('')
        
        fig.text(-.075, 0.45, r'P(k)(Mpc/h)$^{-3}$', ha = 'center', rotation='vertical', fontsize=16)

        fig.text(0.45, -.075, r'k (Mpc/h)$^{-1}$', va = 'center', fontsize=16)
        return

    def HI_galaxy_Xpk_methodology(self, in_rss = False, panel_length = 3, panel_bt = 0.1, text_space = 0.1):
        """
        HI-galaxy cross powers separated into different panels by their methodologies.
        This plot is designed to go into the results section of the paper.

        Dependencies: hiptl, hisubhalo, vn, galaxy
        """
        # get the needed fields
        hiptls = self._fetchResults('hiptlXgalaxy')
        hisubs = self._fetchResults('hisubhaloXgalaxy')
        vns = self._fetchResults('vnXgalaxy')

        # get the desired keys for each field
        colors = ['red', 'blue']
        vnkeys = {}
        hiptlkeys = {}
        hisubkeys = {}
        for c in colors:
            if not in_rss:
                vnkeys[c] = self._rmKeys(['rs'], list(vns[0].pks.keys()))
                vnkeys[c] = self._fetchKeys([c], vnkeys[c])
                hiptlkeys[c] = self._rmKeys(['rs'], list(hiptls[0].pks.keys()))
                hiptlkeys[c] = self._fetchKeys([c], hiptlkeys[c])            
                hisubkeys[c] = self._rmKeys(['rs'], list(hisubs[0].pks.keys()))
                hisubkeys[c] = self._fetchKeys([c], hisubkeys[c])
            else:
                vnkeys[c] = self._fetchKeys(['rs', c], list(vns[0].pks.keys()))
                hiptlkeys[c] = self._fetchKeys(['rs', c], list(hiptls[0].pks.keys()))
                hisubkeys[c] = self._fetchKeys(['rs', c], list(hisubs[0].pks.keys()))
        
        # get the yrange
        yrange = [np.inf, 0]
        fields = []
        fields.extend(hiptls)
        fields.extend(hisubs)
        fields.extend(vns)

        for f in fields:
            if f.fieldname == 'hiptl':
                keys = hiptlkeys['red']
            if f.fieldname == 'hisubhalo':
                keys = hisubkeys['red']
            if f.fieldname == 'vn':
                keys = vnkeys['red']

            for k in keys:
                pkmax = np.max(f.pks[k])
                pkmin = np.min(f.pks[k])
                if pkmax > yrange[1]:
                    yrange[1] = pkmax
                if pkmin < yrange[0]:
                    yrange[0] = pkmin
        del fields

        # get info from the fields to prepare plot
        box = hiptls[0].header['BoxSize']
        snapshots = []
        for f in hiptls:
            if not f.snapshot in snapshots:
                snapshots.append(f.snapshot)
        
        # put snapshots in increasing order
        snapshots.sort()
        
        # creating figure
        nrows = len(snapshots)
        ncols = 3 # for each methodology
        figwidth = panel_length * ncols + panel_bt * (ncols - 1)
        figheight = panel_length * nrows + panel_bt * (nrows - 1)
        fig = plt.figure(figsize = (figwidth, figheight))

        # creating gridspec
        gs = gspec.GridSpec(nrows, ncols)
        plt.subplots_adjust(left = panel_bt / figwidth,
                right = 1 - panel_bt / figwidth, top = 1 - panel_bt / figwidth,
                bottom = panel_bt/figwidth, wspace = panel_bt, hspace = panel_bt)

        # now creating panels in order of increasing redshift
        panels = []
        for i in range(nrows):
            col_panels = []
            for j in range(ncols):
                col_panels.append(fig.add_subplot(gs[i,j]))
            panels.append(fig.add_subplot(gs[i]))
        
        for i in range(nrows):
            # make the hisubhalo plot for this redshift
            plt.sca(panels[i][0])
            plib.fillpks(hisubs[i].pks['k'], hisubs[i].pks, box, hisubs[i].resolution,
                    keylist = hisubkeys['blue'], color = 'blue', label = 'Blue Galaxies')

            plib.fillpks(hisubs[i].pks['k'], hisubs[i].pks, box, hisubs[i].resolution,
                    keylist = hisubkeys['red'], color = 'red', label = 'Red Galaxies')
            
            plt.ylim(yrange[0], yrange[1])
            
            # cosmetic tasks
            plt.text(hisubs[i].pks['k'][0]+text_space, yrange[0] + text_space, 'z=%.1f'%snapshots[i],
                    fontsize = 20, ha = 'left', va = 'bottom', fontweight = 'bold')


            ax = plt.gca()
            plt.ylabel('')
            if i == 0:
                ax.xaxis.set_label_position('top')
                plt.xlabel('D18-Subhalo', fontsize=16)
                plt.legend(loc = 'upper right')
            else:
                plt.xlabel('')
                ax.get_legend().remove()

            # make the hiptl plot
            plt.sca(panels[i][1])
            plib.fillpks(hiptls[i].pks['k'], hiptls[i].pks, box, hiptls[i].resolution,
                    keylist = hiptlkeys['blue'], color = 'blue', label = 'Blue Galaxies')

            plib.fillpks(hiptls[i].pks['k'], hiptls[i].pks, box, hiptls[i].resolution,
                    keylist = hiptlkeys['red'], color = 'red', label = 'Red Galaxies')
            plt.ylim(yrange[0], yrange[1])
            
            # cosmetic tasks
            ax = plt.gca()
            plt.ylabel('')
            ax.set_yticklabels([])
            ax.get_legend().remove()
            if i == 0:
                ax.xaxis.set_label_position('top')
                plt.xlabel('D18-Particle', fontsize=16)
                plt.legend(loc = 'upper right')
            else:
                plt.xlabel('')
            # make the vn plot
            plt.sca(panels[i][2])
            plib.plotpks(vns[i].pks['k'], vns[i].pks, box, vns[i].resolution,
                    keylist = vnkeys['blue'], colors = ['blue'], labels = ['Blue Galaxies'])

            plib.plotpks(vns[i].pks['k'], vns[i].pks, box, vns[i].resolution,
                    keylist = vnkeys['red'], colors = ['red'], labels = ['Red Galaxies'])
            plt.ylim(yrange[0], yrange[1])

            # cosmetic tasks
            ax = plt.gca()
            plt.ylabel('')
            ax.set_yticklabels([])
            ax.get_legend().remove()
            if i == 0:
                ax.xaxis.set_label_position('top')
                plt.xlabel('VN18', fontsize=16)
                plt.legend(loc = 'upper right')
            else:
                plt.xlabel('')
        
        fig.text(-.075, 0.45, r'P(k)(Mpc/h)$^{-3}$', ha = 'center', rotation='vertical', fontsize=16)

        fig.text(0.45, -.075, r'k (Mpc/h)$^{-1}$', va = 'center', fontsize=16)
        return

    def HI_galaxy_Xpk_color(self, in_rss = False, panel_length = 3, panel_bt = 0.1, text_space = 0.1):
        """
        HI-galaxy cross powers separated into different panels by their colors.
        Made for both redshift-space and real-space.
        This plot is designed to go into the methods section of the paper.

        Dependencies: hiptl, hisubhalo, vn, galaxy
        """
        # get the needed results
        hiptls = self._fetchResults('hiptlXgalaxy')
        hisubs = self._fetchResults('hisubhaloXgalaxy')
        vns = self._fetchResults('vnXgalaxy')

        colors = ['red', 'blue', 'resolved']
        vnkeys = {}
        hiptlkeys = {}
        hisubkeys = {}
        for c in colors:
            if not in_rss:
                vnkeys[c] = self._rmKeys(['rs'], list(vns[0].pks.keys()))
                vnkeys[c] = self._fetchKeys([c], vnkeys[c])
                hiptlkeys[c] = self._rmKeys(['rs'], list(hiptls[0].pks.keys()))
                hiptlkeys[c] = self._fetchKeys([c], hiptlkeys[c])            
                hisubkeys[c] = self._rmKeys(['rs'], list(hisubs[0].pks.keys()))
                hisubkeys[c] = self._fetchKeys([c], hisubkeys[c])
            else:
                vnkeys[c] = self._fetchKeys(['rs', c], list(vns[0].pks.keys()))
                hiptlkeys[c] = self._fetchKeys(['rs', c], list(hiptls[0].pks.keys()))
                hisubkeys[c] = self._fetchKeys(['rs', c], list(hisubs[0].pks.keys()))
        
        # get the yrange
        yrange = [np.inf, 0]
        fields = []
        fields.extend(hiptls)
        fields.extend(hisubs)
        fields.extend(vns)

        for f in fields:
            if f.fieldname == 'hiptl':
                keys = hiptlkeys['red']
            if f.fieldname == 'hisubhalo':
                keys = hisubkeys['red']
            if f.fieldname == 'vn':
                keys = vnkeys['red']

            for k in keys:
                pkmax = np.max(f.pks[k])
                pkmin = np.min(f.pks[k])
                if pkmax > yrange[1]:
                    yrange[1] = pkmax
                if pkmin < yrange[0]:
                    yrange[0] = pkmin
        del fields

        # get info from the fields to prepare plot
        box = hiptls[0].header['BoxSize']
        snapshots = []
        for f in hiptls:
            if not f.snapshot in snapshots:
                snapshots.append(f.snapshot)
        
        # put snapshots in increasing order
        snapshots.sort()
        
        # creating figure
        nrows = len(snapshots)
        ncols = len(colors)
        figwidth = panel_length * ncols + panel_bt * (ncols - 1)
        figheight = panel_length * nrows + panel_bt * (nrows - 1)
        fig = plt.figure(figsize = (figwidth, figheight))

        # creating gridspec
        gs = gspec.GridSpec(nrows, ncols)
        plt.subplots_adjust(left = panel_bt / figwidth,
                right = 1 - panel_bt / figwidth, top = 1 - panel_bt / figwidth,
                bottom = panel_bt/figwidth, wspace = panel_bt, hspace = panel_bt)

        # now creating panels in order of increasing redshift
        panels = []
        for i in range(nrows):
            col_panels = []
            for j in range(ncols):
                col_panels.append(fig.add_subplot(gs[i,j]))
            panels.append(fig.add_subplot(gs[i]))
        
        for i in range(nrows):

            # make the red plot for this redshift
            plt.sca(panels[i][0])

            plib.fillpks(hisubs[i].pks['k'], hisubs[i].pks, box, hisubs[i].resolution,
                    keylist = hisubkeys['red'], color = 'red', label = 'D18-Subhalo')
            
            plib.fillpks(hiptls[i].pks['k'], hiptls[i].pks, box, hiptls[i].resolution,
                    keylist = hiptlkeys['red'], color = 'lightcoral', label = 'D18-Particle')
            
            
            plib.plotpks(vns[i].pks['k'], vns[i].pks, box, vns[i].resolution,
                    keylist = vnkeys['blue'], colors = ['darkred'], label = ['VN18-Particle'])
            
            plt.ylim(yrange[0], yrange[1])
            
            # cosmetic tasks
            plt.text(hisubs[i].pks['k'][0]+text_space, yrange[0] + text_space, 'z=%.1f'%snapshots[i],
                    fontsize = 20, ha = 'left', va = 'bottom', fontweight = 'bold')


            ax = plt.gca()
            plt.ylabel('')
            if i == 0:
                ax.xaxis.set_label_position('top')
                plt.xlabel('HI-Red Cross-Power', fontsize=16)
                plt.legend(loc = 'upper right')
            else:
                plt.xlabel('')
                ax.get_legend().remove()

            # make the blue plot
            plt.sca(panels[i][1])
            plib.fillpks(hisubs[i].pks['k'], hisubs[i].pks, box, hisubs[i].resolution,
                    keylist = hisubkeys['blue'], color = 'blue', label = 'D18-Subhalo')
            
            plib.fillpks(hiptls[i].pks['k'], hiptls[i].pks, box, hiptls[i].resolution,
                    keylist = hiptlkeys['red'], color = 'teal', label = 'D18-Particle')


            plib.plotpks(vns[i].pks['k'], vns[i].pks, box, vns[i].resolution,
                    keylist = vnkeys['red'], colors = ['purple'], label = ['VN18-Particle'])
            plt.ylim(yrange[0], yrange[1])
            
            # cosmetic tasks
            ax = plt.gca()
            plt.ylabel('')
            ax.set_yticklabels([])
            ax.get_legend().remove()
            if i == 0:
                ax.xaxis.set_label_position('top')
                plt.xlabel('HI-Blue Cross-Power', fontsize=16)
                plt.legend(loc = 'upper right')
            else:
                plt.xlabel('')
            # make the resolved plot
            plt.sca(panels[i][2])
            plib.plotpks(vns[i].pks['k'], vns[i].pks, box, vns[i].resolution,
                    keylist = vnkeys['resolved'], colors = ['darkgreen'], labels = ['VN18-Particle'])

            plib.fillpks(hiptls[i].pks['k'], hiptls[i].pks, box, hiptls[i].resolution,
                    keylist = hiptlkeys['resolved'], color = 'palegreen', label = 'D18-Particle')

            plib.fillpks(hisubs[i].pks['k'], hisubs[i].pks, box, hisubs[i].resolution,
                    keylist = hisubkeys['resolved'], color = 'green', label = 'D18-Subhalo')
            
            plt.ylim(yrange[0], yrange[1])

            # cosmetic tasks
            ax = plt.gca()
            plt.ylabel('')
            ax.set_yticklabels([])
            ax.get_legend().remove()
            if i == 0:
                ax.xaxis.set_label_position('top')
                plt.xlabel('VN18', fontsize=16)
                plt.legend(loc = 'upper right')
            else:
                plt.xlabel('')
        
        fig.text(-.075, 0.45, r'P(k)(Mpc/h)$^{-3}$', ha = 'center', rotation='vertical', fontsize=16)

        fig.text(0.45, -.075, r'k (Mpc/h)$^{-1}$', va = 'center', fontsize=16)
        return

    def gr_stmass(self, snapshot = 99, panel_length = 8, panel_bt = 0.1, cbar_width = 1):
        galaxy = self._fetchResults('galaxy', snapshot)
        galaxy_dust = self._fetchResults('galaxy_dust', snapshot)
        nrows = 1
        nhist = 2
        ncols = panel_length*nhist + cbar_width
        # create the figure with the right dimensions
        figwidth = panel_length * nhist + panel_bt * (nhist - 1) + cbar_width
        figheight = panel_length * nrows + panel_bt * (nrows - 1)
        fig = plt.figure(figsize = (figwidth, figheight))

        # creating gridspec
        gs = gspec.GridSpec(nrows, ncols)
        plt.subplots_adjust(left = panel_bt / figwidth,
                right = 1 - panel_bt / figwidth, top = 1 - panel_bt / figwidth,
                bottom = panel_bt/figwidth, wspace = panel_bt, hspace = panel_bt)
        
        panels = []
        panels.append(fig.add_subplot(gs[:panel_length]))
        panels.append(fig.add_subplot(gs[panel_length:panel_length*2]))
        panels.append(fig.add_subplot(gs[panel_length*2:panel_length*2+cbar_width]))

        # for the color cut lines
        xmin = min(np.min(galaxy.gr[1]), np.min(galaxy_dust.gr[1]))
        xmax = max(np.max(galaxy.gr[1]), np.max(galaxy_dust.gr[1]))
        ymin = min(np.min(galaxy.gr[2]), np.min(galaxy_dust.gr[2]))
        ymax = max(np.max(galaxy.gr[2]), np.max(galaxy_dust.gr[2]))
        x = np.linspace(xmin, xmax)

        # functions for the color cuts
        col_defs = galaxy.getColorDefinitions()
        funcs = {}
        for k,v in col_defs.items():
            funcs[k] = lambda x: v['b'] + (v['m'] * x + v['mb'])
        
        plt.sca(panels[0])

        plt.imshow(np.rot90(galaxy.gr[0]), norm=mpl.colors.LogNorm(), 
                extent=(xmin, xmax, ymin, ymax))
        
        for k,v in funcs.items():
            plt.plot(x, v(x), label=k)
        
        plt.ylabel('g-r (magnitude)')
        ax = plt.gca()
        ax.xaxis.set_label_position('top')
        plt.xlabel('No Dust', fontsize = 16)
        plt.legend()
        plt.sca(panels[1])
        plt.imshow(np.rot90(galaxy_dust.gr[0]), norm=mpl.colors.LogNorm(), 
                extent=(xmin, xmax, ymin, ymax))
        
        ax = plt.gca()
        ax.xaxis.set_label_position('top')
        plt.xlabel('Dust-Attenuated', fontsize = 16)
        ax.set_yticklabels([])
        for k,v in funcs.items():
            plt.plot(x, v(x), label=k)

        plt.sca(panels[2])
        ax = plt.gca()
        plt.colorbar(cax=ax)
        fig.text(0.45, -.075, r'log($M_{*}$)', va = 'center', fontsize=16)

        plt.title("Color-Stellar Mass for z=%.1f"%galaxy.snapshot)
        return

    def gr_hist(self, snapshot = 99, panel_length = 8, panel_bt = 0.1):
        ################## HELPER FUNCTION #####################
        def get_hist(gr):
            mid = []
            for i in range(len(gr[2])-1):
                mid.append((gr[2][i] + gr[2][i+1]) / 2)
            hist = np.sum(gr[0], axis=0)
            return np.array(mid), hist
        ########################################################

        galaxy = self._fetchResults('galaxy', snapshot)
        galaxy_dust = self._fetchResults('galaxy_dust', snapshot)
        nrows = 1
        ncols = 2

        # create the figure with the right dimensions
        figwidth = panel_length * ncols + panel_bt * (ncols - 1)
        figheight = panel_length * nrows + panel_bt * (nrows - 1)
        fig = plt.figure(figsize = (figwidth, figheight))

        # creating gridspec
        gs = gspec.GridSpec(nrows, ncols)
        plt.subplots_adjust(left = panel_bt / figwidth,
                right = 1 - panel_bt / figwidth, top = 1 - panel_bt / figwidth,
                bottom = panel_bt/figwidth, wspace = panel_bt, hspace = panel_bt)
        
        panels = []
        panels.append(fig.add_subplot(gs[:panel_length]))
        panels.append(fig.add_subplot(gs[panel_length:panel_length*2]))

        # getting the lines
        col_defs = galaxy.getColorDefinitions()
        vals = {}
        for k,v in col_defs.items():
            if v['m'] == 0:
                vals[k] = v['b']
        
        # getting the histograms
        dustx, dusthist = get_hist(galaxy_dust.gr)
        x, hist = get_hist(galaxy.gr)
        ymin = 0
        ymax = max(np.max(dusthist), np.max(hist))

        # getting the bar colors
        threshold = vals['straight']
        rgb = np.zeros([x.shape[0], 3])
        rgb[:,0] = 1/(x[-1] - threshold) * (x - threshold)
        rgb[:,2] = 1/(x[0] - threshold) * (x - threshold)
        # rgb[:,1] = (0.5-rgb[:,0]-rgb[:,2]) * 0.75
        # making the first panel
        plt.sca(panels[0])
        plt.bar(x, hist, width=x[1] - x[0], color=rgb)
        plt.ylim(ymin, ymax)
        plt.ylabel(r'N$_{\rm gal}$')
        ax = plt.gca()
        ax.xaxis.set_label_position('top')
        plt.xlabel('No Dust', fontsize = 16)

        for k,v in vals.items():
            plt.plot((v,v),(ymin, ymax), label = '%.2f'%v, linestyle='--')
        
        plt.legend()
        # making the second panel
        plt.sca(panels[1])
        plt.bar(dustx, dusthist, width=x[1] - x[0], color=rgb)
        plt.ylim(ymin, ymax)
        ax = plt.gca()
        ax.xaxis.set_label_position('top')
        plt.xlabel('Dust-Attenuated', fontsize = 16)
        ax.set_yticklabels([])
        for k,v in vals.items():
            plt.plot((v,v),(ymin, ymax), label = '%.2f'%v, linestyle='--')
        fig.text(0.45, -.075, r'g-r (magnitude)', va = 'center', fontsize=16)

        plt.title("Color Histogram for z=%.1f"%galaxy.snapshot)
        return

def galaxy_auto_pk():
    return

def stmass_vs_all_mass():
    return

def hiptl_nh_pk():
    return

def grid_resolution_test():
    return

def color_def_sensitivity():
    return

def galaxy_galaxy_xpk():
    return

def cicw_vs_cic():
    return

def HI_ptl_Xpk():
    return

def dust_sensitivity():
    return

def sim_resolution_test():
    return
