from hc_lib.plots import plot_lib as plib
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import sys

mpl.rcParams['text.usetex'] = True

def main():
    print("loading paths...")
    OUTDIR = sys.argv.pop(1)
    paths = plib.getPaths(OUTDIR)

    print("loading pickle files...")
    gals = plib.checkPkls(paths, {'fieldname':'galaxy'})
    gdusts = plib.checkPkls(paths, {'fieldname':'galaxy_dust'})

    print("comparing dust sensitivity in the auto power...")
    dust_sensitivity(gals, gdusts)

    print("comparing stmass and all mass auto power...")
    stmass_vs_total(gals)

    print("comparing results from different color cuts...")
    color_cuts(gals)

    print("now making evolution of galaxy auto power as a function of redshift...")
    galaxy_auto(gals)
    return

def galaxy_auto(gals):
    return

def color_cuts(gals):
    return

def stmass_vs_total(gals):
    return

def dust_sensitivity(gals, gdusts, panel_length = 3, 
        panel_bt = 0.1, border = 0.5, fsize=16):
    snapshots, redshifts = plib.getSnaps(gals + gdusts)
    
    def match_snapshot(snapshot, fields):
        for f in fields:
            if snapshot == f.snapshot:
                return f
        return None

    # plotting mass_type vs space
    col_labels = ['real space', 'redshift space']
    row_labels = ['stellar mass', 'all mass']
    nrows = len(row_labels)
    ncols = len(col_labels)
    xborder = [1.5*border, border]
    yborder = [border, 1.5*border]
    for s in range(len(snapshots)):
        fig, panels = plib.createFig(panel_length, nrows, ncols, panel_bt, 
                xborder, yborder)
        snap = snapshots[s]
        z = redshifts[s]
        gal = match_snapshot(snap, gals)
        gdust = match_snapshot(snap, gdusts)
        galkeys = list(gal.pks.keys())
        galst_keys = plib.fetchKeys(['stmass', 'CICW', '0.6'], 
                ['rs', 'papa'], galkeys)
        galst_keys.append('resolved_CICW_stmass')
        galtot_keys = plib.fetchKeys(['total', 'CICW', '0.6'], 
                ['rs', 'papa'], galkeys)
        galtot_keys.append('resolved_CICW_total')
        plot_key_dict = {'stellar mass':galst_keys, 'all mass':galtot_keys}
        for i in range(nrows):
            for j in range(ncols):
                plt.sca(panels[i][j])

                plot_keys = plot_key_dict[row_labels[i]]
                if col_labels[j] == 'redshift space':
                    plot_keys = [pkey + 'rs' for pkey in plot_keys]
                colors = []
                for pkey in plot_keys:
                    if 'red' in pkey:
                        colors.append('red')
                    elif 'blue' in pkey:
                        colors.append('blue')
                    elif 'resolved' in pkey:
                        colors.append('green')
                    
                plib.plotpks(gal.pks['k'], gal.pks, gal.box, gal.resolution,
                        plot_keys, colors=colors)
                
                linestyles = ['--']*len(plot_keys)
                plib.plotpks(gdust.pks['k'], gdust.pks, gdust.box, gdust.resolution,
                        plot_keys, colors, linestyles=linestyles)
        
    return
if __name__ == '__main__':
    main()
