from matplotlib import lines
from hc_lib.plots import plot_lib as plib
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import sys

from hc_lib.plots.figures.slices import get_suffix

mpl.rcParams['text.usetex'] = True

def main():
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

    print("comparing stmass and all mass auto power...")
    stmass_vs_total(gals)

    print("comparing results from different color cuts...")
    color_cuts(gals)

    print("now making evolution of galaxy auto power as a function of redshift...")
    galaxy_auto(gals)
    return

def get_suffix(field):
    tup = (field.simname, field.snapshot, field.axis, field.resolution)
    suf = "%sB_%03dS_%dA_%dR"%tup
    return suf

def galaxy_auto(gals):
    return

def color_cuts(gals):
    return

def stmass_vs_total(gals):
    return
def dust_sensitivity_galaxy_resolution(gals, gdusts):
    return

def dust_sensitivity_color_cut(gals, gdusts):
    return

def dust_sensitivity_stmass(gals, gdusts, panel_length = 3, 
        panel_bt = 0.1, border = 1, fsize=16):
    snapshots, redshifts = plib.getSnaps(gals + gdusts)
    
    def match_snapshot(snapshot, fields):
        for f in fields:
            if snapshot == f.snapshot:
                return f
        return None

    # plotting mass_type vs space
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
        
        plot_key_dict = {'Stellar Mass':galst_keys, 'All Species':galtot_keys}
        for j in range(ncols):
            plt.sca(panels[i][j])
            colors = []
            if not j == ncols - 1:
                labels = []
                pkeys = plot_key_dict[col_labels[j]]
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
                ax = plt.gca()
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
                        labels.append('Red Galaxies')
                        colors.append('red')
                    elif 'blue' 
                        labels.append('Blue Galaxies')
                        color.append('blue')
                    
                for l in labels:
                    if 'Red' in l:
                        colors.append('red')
                    elif 'Blue' in l:
                        colors.append('blue')
                    if 'Stellar' in l:
                        linestyles.append('--')
                    elif 'All' in l:
                        linestyles.append('-')
                pkeys = galst_keys + galtot_keys
                for pkey in pkeys:
                    ratio_pks[pkey] = gal.pks[pkey]/gdust.pks[pkey]

                plib.plotpks(gal.pks['k'], ratio_pks, gal.box, gal.resolution, 
                        pkeys, colors = colors, labels = labels, linestyles = linestyles)
                plt.yscale('linear')
                 
            ax = plt.gca()
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
                plt.ylabel(r'$\frac{P_{gal}(k)}{P_{dust}(k)}$')
            
            if not j == 0 or not j == ncols - 1:
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
        panel_bt = 0.1, border = 1, fsize=16):
    snapshots, redshifts = plib.getSnaps(gals + gdusts)
    
    def match_snapshot(snapshot, fields):
        for f in fields:
            if snapshot == f.snapshot:
                return f
        return None

    # plotting mass_type vs space
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
                if col_labels[i] == 'Real Space':
                    pkeys = galst_keys
                elif col_labels[i] == 'Redshift Space':
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
                labels = ['Red', 'Blue', 'All', 'Redshift Space', '', '']
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
                        linestyles.append('--')
                    else:
                        linestyles.append('-')
                
                for pkey in pkeys:
                    ratio_pks[pkey] = gal.pks[pkey]/gdust.pks[pkey]

                plib.plotpks(gal.pks['k'], ratio_pks, gal.box, gal.resolution, 
                        pkeys, colors = colors, labels = labels, linestyles = linestyles)
            
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
                plt.ylabel(r'$\frac{P_{gal}(k)}{P_{dust}(k)}$')
            
            if not j == 0 or not j == ncols - 1:
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
