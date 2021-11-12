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
        panel_bt = 0.1, border = 1, fsize=16):
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
    #xborder = [1.5*border, border]
    #yborder = [border, 1.5*border]
    for s in range(len(snapshots)):
        fig, panels = plib.createFig(panel_length, nrows, ncols, panel_bt, 
                border, border)
        snap = snapshots[s]
        z = redshifts[s]
        gal = match_snapshot(snap, gals)
        gdust = match_snapshot(snap, gdusts)
        galkeys = list(gal.pks.keys())
        galst_keys = plib.fetchKeys(['stmass', 'CICW', '0.6'], 
                ['rs', 'papa', '0.65'], galkeys)
        #galst_keys.append('resolved_CICW_stmass_diemer')
        galtot_keys = plib.fetchKeys(['total', 'CICW', '0.6'], 
                ['rs', 'papa', '0.65'], galkeys)
        #galtot_keys.append('resolved_CICW_total_diemer')
        plot_key_dict = {'stellar mass':galst_keys, 'all mass':galtot_keys}

        
        yrange = [np.inf, 0]
        #print("keys being used...")
        for i in range(nrows):
            for j in range(ncols):
                plt.sca(panels[i][j])
                plot_keys = plot_key_dict[row_labels[i]]
                if col_labels[j] == 'redshift space':
                    plot_keys = [pkey + 'rs' for pkey in plot_keys]
                colors = []
                labels = []
                for pkey in plot_keys:
                    if 'red' in pkey:
                        colors.append('red')
                        labels.append('Red Galaxies')
                    elif 'blue' in pkey:
                        colors.append('blue')
                        labels.append('Blue Galaxies')
                    elif 'resolved' in pkey:
                        colors.append('green')
                        labels.append('All Galaxies')
                    
                plib.plotpks(gal.pks['k'], gal.pks, gal.box, gal.resolution,
                        plot_keys, labels=labels, colors=colors)
                
                linestyles = ['--']*len(plot_keys)
                plib.plotpks(gdust.pks['k'], gdust.pks, gdust.box, gdust.resolution,
                        plot_keys, labels=['']*len(plot_keys), colors=colors, linestyles=linestyles)



                ax = plt.gca()
                
                ymin, ymax = ax.get_ylim()
                if ymin > 0:
                    yrange[0] = min(yrange[0], ymin)

                yrange[1] = max(yrange[1], ymax)

                if i == 0 and j == 0:
                    plt.legend(loc = 'upper right')
                else:
                    ax.get_legend().remove()

                if i == 0:
                    ax.xaxis.set_label_position('top')
                    plt.xlabel(col_labels[j])
                else:
                    plt.xlabel('')
                    
                if not i == nrows-1:
                    ax.set_xticklabels([])

                if j == 0:
                    plt.ylabel(row_labels[i])
                else:
                    plt.ylabel('')
                    ax.set_yticklabels([])
        for i in range(nrows):
            for j in range(ncols):
                plt.sca(panels[i][j])
                plt.ylim(yrange[0], yrange[1])
        figsize = fig.get_size_inches()
        fig.text(border/3/figsize[0], 0.5, r'P(k) (h/Mpc)$^3$', ha = 'center',
                va = 'center', fontsize = fsize, rotation = 'vertical')
        fig.text(0.5, border/3/figsize[1], r'k (h/Mpc)', ha = 'center',
                va = 'center', fontsize = fsize)
        plt.savefig('dust_sensitivity_mass_type_vs_space%03d.png'%snap)
        plt.clf()
        
    return
if __name__ == '__main__':
    main()
