from hc_lib.plots import plot_lib as plib
import copy
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import sys

from hc_lib.plots.figures.slices import get_suffix

mpl.rcParams['text.usetex'] = True

def main():
    print('_______________MAKING GALAXY AUTO POWER SPECTRA____________')
    print("loading paths...")
    OUTDIR = sys.argv.pop(1)
    paths = plib.getPaths(OUTDIR)

    print("loading pickle files...")
    gals = plib.checkPkls(paths, {'fieldname':'galaxy'})
    gdusts = plib.checkPkls(paths, {'fieldname':'galaxy_dust'})

    print("comparing dust sensitivity in the auto power...")
    dust_sensitivity_stmass(gals, gdusts)
    dust_sensitivity_color_cut(gals, gdusts)
    dust_sensitivity_space(gals, gdusts)
    dust_sensitivity_galaxy_resolution(gals, gdusts)

    print("now making evolution of galaxy auto power as a function of redshift...")
    galaxy_auto_redshift_vs_space(gals)
    return

def get_suffix(field):
    tup = (field.simname, field.snapshot, field.axis, field.resolution)
    suf = "%sB_%03dS_%dA_%dR"%tup
    return suf

def galaxy_auto_redshift_vs_space(gals, panel_length = 3, panel_bt = 0.33, border = 1, fsize = 16):
    snapshots, redshifts = plib.getSnaps(gals)
    
    def match_snapshot(snapshot, fields):
        for f in fields:
            if snapshot == f.snapshot:
                return f
        return None

    # plotting redshift vs space
    col_labels = ['Real Space', 'Redshift Space', 'Redshift Space Distortions']
    nrows = len(snapshots)
    ncols = len(col_labels)
    fig, panels = plib.createFig(panel_length, nrows, ncols, [panel_bt*1.5, panel_bt], 
        border, border)
    
    yrange = [np.inf, 0]

    for i in range(nrows):
        snap = snapshots[i]
        gal = match_snapshot(snap, gals)
        for j in range(ncols):
            plt.sca(panels[i][j])
            ax = plt.gca()
            colors = []
            labels = []
            #print(list(gal.pks.keys()))
            pkeys = plib.fetchKeys(['0.6', 'stmass','CICW'], ['rs','0.65','papa', 'all', 'eBOSS'], list(gal.pks.keys()))
            pkeys.append('resolved_CICW_stmass_diemer')
            if col_labels[j] == 'Redshift Space':
                pkeys = [pkey + 'rs' for pkey in pkeys]
            for pkey in pkeys:
                if 'red' in pkey:
                    colors.append('red')
                    labels.append('Red Galaxies')
                elif 'blue' in pkey:
                    colors.append('blue')
                    labels.append('Blue Galaxies')
                elif 'resolved' in pkey:
                    colors.append('green')
                    labels.append('All Galaxies')
                
            
            if col_labels[j] == 'Redshift Space Distortions':
                ratio_pks = {}
                for pkey in pkeys:
                    ratio_pks[pkey] = gal.pks[pkey+'rs']/gal.pks[pkey]
                plib.plotpks(gal.pks['k'], ratio_pks, gal.box, gal.resolution,
                        pkeys, colors, labels)
                plt.yscale('linear')
            else:
                plib.plotpks(gal.pks['k'], gal.pks, gal.box, gal.resolution, pkeys,
                        colors, labels)
                ymin, ymax = ax.get_ylim()
                if ymin > 0:
                    yrange[0] = min(yrange[0], ymin)

                yrange[1] = max(yrange[1], ymax)
                        
            plt.ylabel('')

            if i == 0:
                ax.xaxis.set_label_position('top')
                plt.xlabel(col_labels[j])
                plt.legend(loc = 'upper right')
            else:
                plt.xlabel('')
                ax.get_legend().remove()
                ax.set_xticklabels([])
            
            if j == 0:
                plt.text(0.05, 0.05,
                    'z=%.1f'%redshifts[i], fontsize = fsize, ha = 'left', va = 'bottom',
                    fontweight = 'bold', transform = ax.transAxes)
            elif j == ncols - 1:
                plt.ylabel(r'$\frac{P_{z}(k)}{P_{r}(k)}$', fontsize=fsize)
                ax.get_legend().remove()
            else:
                ax.set_yticklabels([])
                ax.get_legend().remove()


    for i in range(nrows):
        for j in range(ncols):
            if i < nrows - 1 and j < ncols - 1:
                plt.sca(panels[i][j])
                plt.ylim(yrange[0], yrange[1])
    figsize = fig.get_size_inches()
    fig.text(border/3/figsize[0], 0.5, r'P(k) (h/Mpc)$^3$', ha = 'center',
            va = 'center', fontsize = fsize, rotation = 'vertical')
    fig.text(0.5, border/3/figsize[1], r'k (h/Mpc)', ha = 'center',
            va = 'center', fontsize = fsize)
    plt.savefig('galaxy_auto_redshift_vs_space_%s.png'%get_suffix(gal))
    plt.clf()      

    return


def dust_sensitivity_galaxy_resolution(gals, gdusts):
    return


def dust_sensitivity_color_cut(gals, gdusts, panel_length = 3, 
        panel_bt = 0.33, border = 1, fsize=16):
    snapshots, redshifts = plib.getSnaps(gals + gdusts)
    
    def match_snapshot(snapshot, fields):
        for f in fields:
            if snapshot == f.snapshot:
                return f
        return None

    # plotting redshift vs different color cuts
    
    col_labels = gals[0].getColorDefinitions()
    col_labels.append('Straight Cut Ratios')
    col_labels.append('Observational Cut Ratios')
    nrows = len(snapshots)
    ncols = len(col_labels)
    fig, panels = plib.createFig(panel_length, nrows, ncols, panel_bt, 
        border, border)
    
    yrange = [np.inf, 0]
    for i in range(nrows):
        snap = snapshots[i]
        gal = match_snapshot(snap, gals)
        gdust = match_snapshot(snap, gdusts)
        galkeys = list(gal.pks.keys())

        for j in range(ncols):
            plt.sca(panels[i][j])

            colors = []
            labels = []
            ax = plt.gca()

            if j < ncols - 2:
                cut = col_labels[j]
                other_cuts = copy.copy(col_labels)
                other_cuts.remove(cut)
                
                if cut == '0.65' or cut == "0.55":
                    other_cuts.remove(cut[:-1])
                    pkeys = plib.fetchKeys([cut, 'stmass', 'CICW'], ['rs', 'resolved'] + other_cuts, galkeys)
                else:
                    pkeys = plib.fetchKeys([cut, 'stmass', 'CICW'], other_cuts + ['rs', 'resolved'], galkeys)
                    linestyles_dust = ['--']*len(pkeys)

                for pkey in pkeys:
                    if 'red' in pkey:
                        colors.append('red')
                        labels.append('Red Galaxies')
                    elif 'blue' in pkey:
                        colors.append('blue')
                        labels.append('Blue Galaxies')
                
                if j == 0:
                    plib.plotpks(gal.pks['k'], gal.pks, gal.box, gal.resolution,
                            pkeys, colors=colors, labels=labels)
                    plib.plotpks(gdust.pks['k'], gdust.pks, gdust.box, gdust.resolution,
                        pkeys, labels=['']*len(pkeys), colors=colors, linestyles=linestyles_dust)
                elif j == 1:
                    labels = [''] * (len(pkeys) - 1)
                    plib.plotpks(gal.pks['k'], gal.pks, gal.box, gal.resolution,
                            pkeys, colors=colors, labels=['No Dust'] + labels)
                    plib.plotpks(gdust.pks['k'], gdust.pks, gdust.box, gdust.resolution,
                        pkeys, labels=['With Dust']+labels, colors=colors, linestyles=linestyles_dust)
                else:
                    plib.plotpks(gal.pks['k'], gal.pks, gal.box, gal.resolution, pkeys, colors=colors,
                            labels=['']*len(pkeys))
                    plib.plotpks(gdust.pks['k'], gdust.pks, gdust.box, gdust.resolution, pkeys, colors=colors,
                            labels=['']*len(pkeys), linestyles=linestyles_dust)
                ymin, ymax = ax.get_ylim()
                if ymin > 0:
                    yrange[0] = min(yrange[0], ymin)

                yrange[1] = max(yrange[1], ymax)
                plt.ylabel('')

            elif j == ncols - 2:
                ratio_pks = {}
                cuts = ['0.6','0.65', '0.55']
                labels = []
                pkeys = []
                for c in cuts:
                    other_cuts = copy.copy(cuts)
                    other_cuts.remove(c)
                    if c == '0.65':
                        other_cuts.remove('0.6')
                    pkeys += plib.fetchKeys([c, 'stmass'], other_cuts+['rs', 'resolved'], galkeys)
                linestyles = []
                for pkey in pkeys:
                    if 'red' in pkey:
                        colors.append('red')
                    elif 'blue' in pkey:
                        colors.append('blue')


                    if '0.55' in pkey:
                        cut_label = 'g-r = 0.55'
                        if cut_label not in labels:
                            labels.append(cut_label)
                        else:
                            labels.append('')
                        linestyles.append(':')
                    if '0.65' in pkey:
                        cut_label = 'g-r = 0.65'
                        if cut_label not in labels:
                            labels.append(cut_label)
                        else:
                            labels.append('')
                        linestyles.append('--')
                    else:
                        cut_label = 'g-r = 0.6'
                        if cut_label not in labels:
                            labels.append(cut_label)
                        else:
                            labels.append('')
                        linestyles.append('-')
                
                for pkey in pkeys:
                    ratio_pks[pkey] = gal.pks[pkey]/gdust.pks[pkey]

                plib.plotpks(gal.pks['k'], ratio_pks, gal.box, gal.resolution, 
                        pkeys, colors = colors, labels = labels, linestyles = linestyles)
            
            elif j == ncols - 1:
                ratio_pks = {}
                cuts = ['0.6','papa']
                labels = []
                pkeys = []
                for c in cuts:
                    other_cuts = copy.copy(col_labels)
                    other_cuts.remove(c)
                    pkeys += plib.fetchKeys([c, 'stmass'], other_cuts+['rs', 'resolved'], galkeys)
                linestyles = []
                for pkey in pkeys:
                    if 'red' in pkey:
                        colors.append('red')
                    elif 'blue' in pkey:
                        colors.append('blue')


                    if 'papa' in pkey:
                        cut_label = 'Papastergis (2013)'
                        if cut_label not in labels:
                            labels.append(cut_label)
                        else:
                            labels.append('')
                        linestyles.append(':')
                    else:
                        cut_label = 'g-r = 0.6'
                        if cut_label not in labels:
                            labels.append(cut_label)
                        else:
                            labels.append('')
                        linestyles.append('-')
                
                for pkey in pkeys:
                    ratio_pks[pkey] = gal.pks[pkey]/gdust.pks[pkey]

                plib.plotpks(gal.pks['k'], ratio_pks, gal.box, gal.resolution, 
                        pkeys, colors = colors, labels = labels, linestyles = linestyles)
                plt.yscale('linear')
            if i == 0:
                ax.xaxis.set_label_position('top')
                title = col_labels[j]
                if title == 'papa':
                    title = 'Papastergis (2013)'
                if title == 'nelson':
                    title = 'Nelson (2018)'
                plt.xlabel(title)
                plt.legend(loc = 'upper right')
            else:
                plt.xlabel('')
                ax.get_legend().remove()
                ax.set_xticklabels([])
            
            if j == 0:
                plt.text(0.05, 0.05,
                    'z=%.1f'%redshifts[i], fontsize = fsize, ha = 'left', va = 'bottom',
                    fontweight = 'bold', transform = ax.transAxes)
            elif j == ncols - 1 or j == ncols - 2:
                plt.ylabel(r'$\frac{P_{gal}(k)}{P_{dust}(k)}$', fontsize=fsize)
            
            else:
                ax.set_yticklabels([])


    for i in range(nrows):
        for j in range(ncols):
            if i < nrows - 1 and j < ncols - 1:
                plt.sca(panels[i][j])
                plt.ylim(yrange[0], yrange[1])
    figsize = fig.get_size_inches()
    fig.text(border/3/figsize[0], 0.5, r'P(k) (h/Mpc)$^3$', ha = 'center',
            va = 'center', fontsize = fsize, rotation = 'vertical')
    fig.text(0.5, border/3/figsize[1], r'k (h/Mpc)', ha = 'center',
            va = 'center', fontsize = fsize)
    plt.savefig('dust_sensitivity_color_cut_%s.png'%get_suffix(gal))
    plt.clf()      
    return


def dust_sensitivity_stmass(gals, gdusts, panel_length = 3, 
        panel_bt = 0.33, border = 1, fsize=16):
    snapshots, redshifts = plib.getSnaps(gals + gdusts)
    
    def match_snapshot(snapshot, fields):
        for f in fields:
            if snapshot == f.snapshot:
                return f
        return None

    # plotting redshift vs mass type
    col_labels = ['Stellar Mass', 'All Species', 'Ratio']
    nrows = len(snapshots)
    ncols = len(col_labels)
    fig, panels = plib.createFig(panel_length, nrows, ncols, panel_bt, 
        border, border)
    
    yrange = [np.inf, 0]
    for i in range(nrows):
        snap = snapshots[i]
        gal = match_snapshot(snap, gals)
        gdust = match_snapshot(snap, gdusts)


        galkeys = list(gal.pks.keys())
        galst_keys = plib.fetchKeys(['stmass', 'CICW', '0.6'], 
                ['rs', 'papa', '0.65'], galkeys)
        galtot_keys = plib.fetchKeys(['total', 'CICW', '0.6'], 
                ['rs', 'papa', '0.65'], galkeys)
        
        plot_key_dict = {'Stellar Mass':galst_keys, 'All Species':galtot_keys, 
                'Ratio':galst_keys + galtot_keys}
        for j in range(ncols):
            plt.sca(panels[i][j])
            colors = []
            ax = plt.gca()
            pkeys = plot_key_dict[col_labels[j]]

            if not j == ncols - 1:
                labels = []
                linestyles_dust = ['--']*len(pkeys)

                for pkey in pkeys:
                    if 'red' in pkey:
                        colors.append('red')
                        labels.append('Red Galaxies')
                    elif 'blue' in pkey:
                        colors.append('blue')
                        labels.append('Blue Galaxies')
                
                if j == 0:
                    plib.plotpks(gal.pks['k'], gal.pks, gal.box, gal.resolution,
                            pkeys, colors=colors, labels=labels)
                    plib.plotpks(gdust.pks['k'], gdust.pks, gdust.box, gdust.resolution,
                        pkeys, labels=['']*len(pkeys), colors=colors, linestyles=linestyles_dust)
                elif j == 1:
                    labels = [''] * (len(pkeys) - 1)
                    plib.plotpks(gal.pks['k'], gal.pks, gal.box, gal.resolution,
                            pkeys, colors=colors, labels=['No Dust'] + labels)
                    plib.plotpks(gdust.pks['k'], gdust.pks, gdust.box, gdust.resolution,
                        pkeys, labels=['With Dust']+labels, colors=colors, linestyles=linestyles_dust)
                ymin, ymax = ax.get_ylim()
                if ymin > 0:
                    yrange[0] = min(yrange[0], ymin)

                yrange[1] = max(yrange[1], ymax)

            else:
                ratio_pks = {}
                labels = []
                linestyles = []
                for pkey in pkeys:
                    ratio_pks[pkey] = gal.pks[pkey]/gdust.pks[pkey]
                    if 'red' in pkey:
                        colors.append('red')
                    elif 'blue' in pkey: 
                        colors.append('blue')
                    
                    if 'stmass' in pkey:
                        stellar_label = 'Stellar'
                        if not stellar_label in labels:
                            labels.append(stellar_label)
                        else:
                            labels.append('')
                        linestyles.append('--')
                    elif 'total' in pkey:
                        total_label = 'All Species'
                        if not total_label in labels:
                            labels.append(total_label)
                        else:
                            labels.append('')
                        linestyles.append('-')
                

                plib.plotpks(gal.pks['k'], ratio_pks, gal.box, gal.resolution, 
                        pkeys, colors = colors, labels = labels, linestyles = linestyles)
                plt.yscale('linear')
                 
            plt.ylabel('')

            if i == 0:
                ax.xaxis.set_label_position('top')
                plt.xlabel(col_labels[j])
                plt.legend(loc = 'upper right')
            else:
                plt.xlabel('')
                ax.get_legend().remove()
                ax.set_xticklabels([])
            
            if j == 0:
                plt.text(0.05, 0.05,
                    'z=%.1f'%redshifts[i], fontsize = fsize, ha = 'left', va = 'bottom',
                    fontweight = 'bold', transform = ax.transAxes)
            elif j == ncols - 1:
                plt.ylabel(r'$\frac{P_{gal}(k)}{P_{dust}(k)}$', fontsize=fsize)
            
            else:
                ax.set_yticklabels([])


    for i in range(nrows):
        for j in range(ncols):
            if i < nrows - 1 and j < ncols - 1:
                plt.sca(panels[i][j])
                plt.ylim(yrange[0], yrange[1])
    figsize = fig.get_size_inches()
    fig.text(border/3/figsize[0], 0.5, r'P(k) (h/Mpc)$^3$', ha = 'center',
            va = 'center', fontsize = fsize, rotation = 'vertical')
    fig.text(0.5, border/3/figsize[1], r'k (h/Mpc)', ha = 'center',
            va = 'center', fontsize = fsize)
    plt.savefig('dust_sensitivity_mass_type_%s.png'%get_suffix(gal))
    plt.clf()      
    return

def dust_sensitivity_space(gals, gdusts, panel_length = 3, 
        panel_bt = 0.5, border = 1, fsize=16):
    snapshots, redshifts = plib.getSnaps(gals + gdusts)
    
    def match_snapshot(snapshot, fields):
        for f in fields:
            if snapshot == f.snapshot:
                return f
        return None

    # plotting redshift vs space
    col_labels = ['Real Space', 'Redshift Space', 'Ratio']
    nrows = len(snapshots)
    ncols = len(col_labels)
    fig, panels = plib.createFig(panel_length, nrows, ncols, panel_bt, 
        border, border)
    
    yrange = [np.inf, 0]
    for i in range(nrows):
        snap = snapshots[i]
        gal = match_snapshot(snap, gals)
        gdust = match_snapshot(snap, gdusts)


        galkeys = list(gal.pks.keys())
        galst_keys = plib.fetchKeys(['stmass', 'CICW', '0.6'], 
                ['rs', 'papa', '0.65'], galkeys)

        
        for j in range(ncols):
            plt.sca(panels[i][j])
            colors = []
            if not j == ncols - 1:
                labels = []
                if col_labels[j] == 'Real Space':
                    pkeys = galst_keys
                elif col_labels[j] == 'Redshift Space':
                    pkeys = [pkey+'rs' for pkey in galst_keys]
                linestyles_dust = ['--']*len(pkeys)

                for pkey in pkeys:
                    if 'red' in pkey:
                        colors.append('red')
                        labels.append('Red Galaxies')
                    elif 'blue' in pkey:
                        colors.append('blue')
                        labels.append('Blue Galaxies')
                    elif 'resolved' in pkey:
                        colors.append('green')
                        labels.append("All Galaxies")
                
                if j == 0:
                    plib.plotpks(gal.pks['k'], gal.pks, gal.box, gal.resolution,
                            pkeys, colors=colors, labels=labels)
                    plib.plotpks(gdust.pks['k'], gdust.pks, gdust.box, gdust.resolution,
                        pkeys, labels=['']*len(pkeys), colors=colors, linestyles=linestyles_dust)
                elif j == 1:
                    labels = [''] * (len(pkeys) - 1)
                    plib.plotpks(gal.pks['k'], gal.pks, gal.box, gal.resolution,
                            pkeys, colors=colors, labels=['No Dust'] + labels)
                    plib.plotpks(gdust.pks['k'], gdust.pks, gdust.box, gdust.resolution,
                        pkeys, labels=['With Dust']+labels, colors=colors, linestyles=linestyles_dust)
                
                ax = plt.gca()
                ymin, ymax = ax.get_ylim()
                if ymin > 0:
                    yrange[0] = min(yrange[0], ymin)

                yrange[1] = max(yrange[1], ymax)

            else:
                ratio_pks = {}
                labels = []
                pkeys = galst_keys + [stkey + 'rs' for stkey in galst_keys]
                linestyles = []
                for pkey in pkeys:
                    if 'red' in pkey:
                        colors.append('red')
                    elif 'blue' in pkey:
                        colors.append('blue')
                    elif 'resolved' in pkey:
                        colors.append('green')

                    if 'rs' in pkey:
                        rss_label = 'Redshift Space'
                        if rss_label not in labels:
                            labels.append(rss_label)
                        else:
                            labels.append('')
                        linestyles.append('--')
                    else:
                        rss_label = 'Real Space'
                        if rss_label not in labels:
                            labels.append(rss_label)
                        else:
                            labels.append('')
                        linestyles.append('-')
                
                for pkey in pkeys:
                    ratio_pks[pkey] = gal.pks[pkey]/gdust.pks[pkey]

                plib.plotpks(gal.pks['k'], ratio_pks, gal.box, gal.resolution, 
                        pkeys, colors = colors, labels = labels, linestyles = linestyles)
                plt.yscale('linear')
            
            ax = plt.gca()
            

            if i == 0:
                ax.xaxis.set_label_position('top')
                plt.xlabel(col_labels[j])
                plt.legend(loc = 'upper right')
            else:
                plt.xlabel('')
                ax.get_legend().remove()
                ax.set_xticklabels([])
            
            if j == 0:
                plt.text(0.05, 0.05,
                    'z=%.1f'%redshifts[i], fontsize = fsize, ha = 'left', va = 'bottom',
                    fontweight = 'bold', transform = ax.transAxes)
            elif j == ncols - 1:
                plt.ylabel(r'$\frac{P_{gal}(k)}{P_{dust}(k)}$', fontsize = fsize)
            
            else:
                ax.set_yticklabels([])


    for i in range(nrows):
        for j in range(ncols):
            if i < nrows - 1 and j < ncols - 1:
                plt.sca(panels[i][j])
                plt.ylim(yrange[0], yrange[1])
    figsize = fig.get_size_inches()
    fig.text(border/3/figsize[0], 0.5, r'P(k) (h/Mpc)$^3$', ha = 'center',
            va = 'center', fontsize = fsize, rotation = 'vertical')
    fig.text(0.5, border/3/figsize[1], r'k (h/Mpc)', ha = 'center',
            va = 'center', fontsize = fsize)
    plt.savefig('dust_sensitivity_space_%s.png'%get_suffix(gal))
    plt.clf()      
    return

if __name__ == '__main__':
    main()
