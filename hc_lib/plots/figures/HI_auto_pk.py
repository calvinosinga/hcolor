
from numpy.lib.type_check import real
from hc_lib.plots import plot_lib as plib
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.gridspec as gspec
import copy
import pickle as pkl
import numpy as np
import sys
from mpl_toolkits.axes_grid1 import make_axes_locatable

mpl.rcParams['text.usetex'] = True

def main():
    
    print("loading paths...")
    OUTDIR = sys.argv.pop(1)
    paths = plib.getPaths(OUTDIR)

    print("loading pickle files...")
    hiptls = plib.checkPkls(paths, {'fieldname':'hiptl'})
    vns = plib.checkPkls(paths, {'fieldname':'vn'})
    hisubs = plib.checkPkls(paths, {'fieldname':'hisubhalo'})

    print("plotting individual models for hiptl...")
    hiptl_individual_models(hiptls)

    print("plotting individual models for hisubhalo...")
    # HI_auto_pk(hiptls, hisubs, vns)


    return


def hiptl_individual_models(hiptls, panel_length = 3, 
            panel_bt = 0.1, border = 0.5, fsize=16):
    
    
    snapshots, redshifts = plib.getSnaps(hiptls)
    nrows = len(snapshots)
    col_labels = ["real space", "redshift space", "comparison"]
    ncols = len(col_labels)

    fig, panels = plib.createFig(panel_length, nrows, ncols, panel_bt,
            border, border)
    
    # getting keys for each part:
    real_keys = plib.fetchKeys([],['rs', 'temp'], list(hiptls[0].keys()))
    redsh_keys = plib.fetchKeys(['rs'], ['temp'], list(hiptls[0].keys()))
    yrange = plib.getYrange(hiptls, real_keys + redsh_keys, False)

    keys = [real_keys, redsh_keys]
    for i in range(nrows):
        snap = snapshots[i]

        for f in hiptls:
            if f.snapshot == snap:
                field = f
                break
        
        for j in range(ncols):
            plt.sca(panels[i][j])
            # comparison column will look different
            colors = ['blue', 'red']
            if j < len(keys):
                labels = [st.split('_')[0] for st in keys[j]]
                print(keys)
                print(labels)
                plib.plotpks(field.pks['k'], field.pks, field.box, field.resolution,
                        keys[j], labels)
                plt.ylim(yrange[0], yrange[1])
            
            else:
                for k in range(len(keys)):
                    plib.fillpks(field.pks['k'], field.pks, field.box, field.resolution,
                            keys[k], label = col_labels[k], color= colors[k])
                plt.legend()
                plt.ylim(yrange[0], yrange[1])
                pk_ax = plt.gca()
                divider = make_axes_locatable(pk_ax)
                frac_ax = divider.append_axes("bottom", size="75%", pad=panel_bt,
                        sharex=pk_ax)
                
                distortions = {}
                for k in keys[0]:
                    distortions[k] = field.pks[k] / field.pks[k+'rs']
                plt.sca(frac_ax)
                plib.fillpks(field.pks['k'], distortions, field.box, field.resolution,
                        keys[0], color='green')
    plt.savefig("hiptl_models_redshift_vs_distortions.png")
    plt.clf()
    return
            

def HI_auto_pk(hiptls, hisubs, vns, panel_length = 3, 
            panel_bt = 0.1, border = 0.5, fsize=16):
    """
    Makes HI-auto power spectra plots, for real space or redshift space.
    Each panel represents another redshift.

    hiptls: list of hiptl objects
    hisubs: list of hisubhalo objects
    vns: list of vn objects
    """

    # get the desired keys for each field - if the fields are not
    # in the results, then make the keys an empty list

    if vns:
        vnkeys = ['vn']
    else:
        vnkeys = []
    if hiptls:
        hiptlkeys = plib.rmKeys(['rs'], list(hiptls[0].pks.keys()))
    else:
        hiptlkeys = []
    if hisubs:
        hisubkeys = plib.rmKeys(['rs'], list(hisubs[0].pks.keys()))
    else:
        hisubkeys = []

    
    fields = []
    fields.extend(hiptls)
    fields.extend(hisubs)
    fields.extend(vns)

    key_dict = {'hiptl':hiptlkeys, 'hisubhalo':hisubkeys, 'vn':vnkeys}
    yrange = plib.getYrange(fields, key_dict)
    snapshots, _ = plib.getSnaps(fields)

    fig, panels = plib.createFig(panel_length, 1, len(snapshots), panel_bt,
            border, border)
    
    print(fig.get_size_inches())
    # now making each panel
    for i in range(len(panels)):
        plt.sca(panels[i])
        panel_snap = snapshots[i]

        # plot the VN18 that matches the panel's redshift
        for pf in vns:
            if pf.snapshot == panel_snap:
                box = pf.header['BoxSize']
                plib.plotpks(pf.pks['k'], pf.pks, box, pf.resolution,
                        keylist = vnkeys, colors = ['green'],
                        labels = ['V-N18'])
        
        # plot the D18-Subhalo that matches the panel's redshift
        for pf in hisubs:
            if pf.snapshot == panel_snap:
                box = pf.header['BoxSize']
                plib.fillpks(pf.pks['k'], pf.pks, box, pf.resolution,
                        keylist = hisubkeys, color = 'orange',
                        label = 'D18-Subhalo')
        
        # plot the D18-Particle that matches the panel's redshift
        for pf in hiptls:
            if pf.snapshot == panel_snap:
                box = pf.header['BoxSize']
                plib.fillpks(pf.pks['k'], pf.pks, box, pf.resolution,
                        keylist = hiptlkeys, color = 'blue',
                        label = 'D18-Particle')

            
        # cosmetic tasks
        if not i == 0:
            ax = plt.gca()
            ax.set_yticklabels([])
            ax.get_legend().remove()
        else:
            plt.legend(loc = 'upper right')
        plt.ylim(yrange[0], yrange[1])
        plt.xlabel('')
        plt.ylabel('')
        # output textbox onto the plot with redshift
        xts = (hiptls[0].pks['k'][0]) / text_space
        yts = (yrange[0]) / text_space
        
        # needed in every panel
        plt.text(hiptls[0].pks['k'][0]+xts, yrange[0]+yts,
                'z=%.1f'%snapshots[i], fontsize = fsize, ha = 'left', va = 'bottom',
                fontweight = 'bold') 

    figsize = fig.get_size_inches()
    fig.text(border/2/figsize[0], 0.5, r'P(k) (Mpc/h)$^{-3}$',ha = 'center',
            va = 'center', fontsize=fsize)
    fig.text(0.5, border/2/figsize[1], r'k (Mpc/h)$^{-1}$', ha = 'center',
            va = 'center', fontsize=fsize)
    return
if __name__ == '__main__':
    main()
