
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
    real_keys = plib.fetchKeys(['CICW'],['rs', 'temp'], list(hiptls[0].pks.keys()))
    redsh_keys = plib.fetchKeys(['rs'], ['temp'], list(hiptls[0].pks.keys()))
    print(real_keys)
    print(redsh_keys)
    keys = {'hiptl':real_keys + redsh_keys}
    yrange = plib.getYrange(hiptls, keys, False)

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
                plib.plotpks(field.pks['k'], field.pks, field.box, field.resolution,
                        keys[j], labels=labels)
                plt.ylim(yrange[0], yrange[1])
            
            else:
                for k in range(len(keys)):
                    plib.fillpks(field.pks['k'], field.pks, field.box, field.resolution,
                            keys[k], label = col_labels[k], color= colors[k])
                plt.legend(loc = 'upper right')
                plt.ylim(yrange[0], yrange[1])
                #pk_ax = plt.gca()
                #divider = make_axes_locatable(pk_ax)
                #frac_ax = divider.append_axes("bottom", size="75%", pad=panel_bt,
                #        sharex=pk_ax)
                
                #distortions = {}
                #for k in keys[0]:
                #    distortions[k] = field.pks[k] / field.pks[k+'rs']
                #plt.sca(frac_ax)
                #plib.fillpks(field.pks['k'], distortions, field.box, field.resolution,
                #        keys[0], color='green')
            ax = plt.gca()
            plt.xlabel('')
            plt.ylabel('')
            if i == 0:
                ax.xaxis.set_label_position('top')
                plt.xlabel(col_labels[j])
            if not i == nrows-1:
                ax.xaxis.set_ticklabels([])
            if j == 0:
                plt.text(field.pks['k'][0], yrange[0]*1.10, '\tz=%.2f'%redshifts[i], 
                        fontsize = fsize, ha = 'left', va = 'bottom')
            else:
                ax.yaxis.set_ticklabels([])
    figsize = fig.get_size_inches()
    fig.text(0.5, border/2/figsize[1], 'k (h/Mpc)', ha='center', va = 'center', 
            fontsize = fsize)

    fig.text(border/2/figsize[0], 0.5, 'P(k) (h/Mpc)$^3$', ha='center', va = 'center', 
            fontsize = fsize, rotation = 'vertical')
    plt.savefig("HI_auto/hiptl_pk_models_redshift_vs_distortions.png")
    plt.clf()
    return
            
def hisubhalo_individual_models(hisubs, panel_length=3, panel_bt = 0.1,
            border = 0.5, fsize = 16):
    snapshots, redshifts = plib.getSnaps(hisubs)
    nrows = len(snapshots)
    col_labels = ["real space", "redshift space", "space comparison"]
    ncols = len(col_labels)

    fig, panels = plib.createFig(panel_length, nrows, ncols, panel_bt,
            border, border)
    
    # getting keys for each part:
    real_keys = plib.fetchKeys(['CICW'],['rs', 'papa'], list(hisubs[0].pks.keys()))
    redsh_keys = plib.fetchKeys(['rs', 'CICW'], ['papa'], list(hisubs[0].pks.keys()))
    print(real_keys)
    print(redsh_keys)
    keys = {'hisubhalo':real_keys + redsh_keys}
    yrange = plib.getYrange(hisubs, keys, False)

    keys = [real_keys, redsh_keys]
    for i in range(nrows):
        snap = snapshots[i]

        for f in hisubs:
            if f.snapshot == snap:
                field = f
                break
        
        for j in range(ncols):
            plt.sca(panels[i][j])
            # comparison column will look different
            colors = ['blue', 'red']
            if j < len(keys):
                labels = [st.split('_')[2] for st in keys[j]]
                plib.plotpks(field.pks['k'], field.pks, field.box, field.resolution,
                        keys[j], labels=labels)
                plt.ylim(yrange[0], yrange[1])
            
            else:
                for k in range(len(keys)):
                    plib.fillpks(field.pks['k'], field.pks, field.box, field.resolution,
                            keys[k], label = col_labels[k], color= colors[k])
                plt.legend(loc = 'upper right')
                plt.ylim(yrange[0], yrange[1])
                #pk_ax = plt.gca()
                #divider = make_axes_locatable(pk_ax)
                #frac_ax = divider.append_axes("bottom", size="75%", pad=panel_bt,
                #        sharex=pk_ax)
                
                #distortions = {}
                #for k in keys[0]:
                #    distortions[k] = field.pks[k] / field.pks[k+'rs']
                #plt.sca(frac_ax)
                #plib.fillpks(field.pks['k'], distortions, field.box, field.resolution,
                #        keys[0], color='green')
            ax = plt.gca()
            plt.xlabel('')
            plt.ylabel('')
            if i == 0:
                ax.xaxis.set_label_position('top')
                plt.xlabel(col_labels[j])
            if not i == nrows-1:
                ax.xaxis.set_ticklabels([])
            if j == 0:
                plt.text(field.pks['k'][0], yrange[0]*1.10, '\tz=%.2f'%redshifts[i], 
                        fontsize = fsize, ha = 'left', va = 'bottom')
            else:
                ax.yaxis.set_ticklabels([])
    figsize = fig.get_size_inches()
    fig.text(0.5, border/2/figsize[1], 'k (h/Mpc)', ha='center', va = 'center', 
            fontsize = fsize)

    fig.text(border/2/figsize[0], 0.5, 'P(k) (h/Mpc)$^3$', ha='center', va = 'center', 
            fontsize = fsize, rotation = 'vertical')
    plt.savefig("HI_auto/hisubhalo_pk_models_redshift_vs_distortions.png")
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

    def match_snapshot(snapshot, fields):
        for f in fields:
            if snapshot == f.snapshot:
                return f
        return None
    
    vn_real_keys = plib.fetchKeys(['mass'], ['rs'], list(vns[0].pks.keys()))
    vn_redsh_keys = plib.fetchKeys(['rs', 'mass'], [], list(vns[0].pks.keys()))
    vn_keys = vn_real_keys + vn_redsh_keys

    hiptl_real_keys = plib.fetchKeys(['mass'], ['rs'], list(hiptls[0].pks.keys()))
    hiptl_redsh_keys = plib.fetchKeys(['mass', 'rs'], [], list(hiptls[0].pks.keys()))
    hiptl_keys = hiptl_redsh_keys + hiptl_real_keys

    hisub_real_keys = plib.fetchKeys(['mass'], ['rs', 'papa'], list(hisubs[0].pks.keys()))
    hisub_redsh_keys = plib.fetchKeys(['mass', 'rs'], ['papa'], list(hisubs[0].pks.keys()))
    hisub_keys = hisub_redsh_keys + hisub_real_keys

    
    fields = []
    fields.extend(hiptls)
    fields.extend(hisubs)
    fields.extend(vns)

    key_dict = {'hiptl':hiptl_keys, 'hisubhalo':hisub_keys, 'vn':vn_keys}
    yrange = plib.getYrange(fields, key_dict)
    snapshots, redshifts = plib.getSnaps(fields)

    col_labels = ['real space', 'redshift space']
    nrows = len(snapshots)
    ncols = len(col_labels)
    fig, panels = plib.createFig(panel_length, nrows, ncols, panel_bt,
            border, border)
    
    # now making each panel
    
    for i in range(nrows):
        snap = snapshots[i]
        vn = match_snapshot(snap, vns)
        hiptl = match_snapshot(snap, hiptls)
        hisub = match_snapshot(snap, hisubs)
        for j in range(ncols):
            plt.sca(panels[i][j])
            if col_labels[j] == 'real space':
                plib.plotpks(vn.pks['k'], vn.pks, vn.box, vn.resolution,
                        keylist = vn_real_keys, colors = ['green'],
                        labels = ['V-N18'])

 
                plib.fillpks(hisub.pks['k'], hisub.pks, hisub.box, hisub.resolution,
                        keylist = hisub_real_keys, color = 'orange',
                        label = 'D18-Subhalo')
                
                plib.fillpks(hiptl.pks['k'], hiptl.pks, hiptl.box, hiptl.resolution,
                        keylist = hiptl_real_keys, color = 'blue',
                        label = 'D18-Subhalo')
            elif col_labels[j] == 'redshift space':
                plib.plotpks(vn.pks['k'], vn.pks, vn.box, vn.resolution,
                        keylist = vn_real_keys, colors = ['green'],
                        labels = ['V-N18'])

 
                plib.fillpks(hisub.pks['k'], hisub.pks, hisub.box, hisub.resolution,
                        keylist = hisub_real_keys, color = 'orange',
                        label = 'D18-Subhalo')
                
                plib.fillpks(hiptl.pks['k'], hiptl.pks, hiptl.box, hiptl.resolution,
                        keylist = hiptl_real_keys, color = 'blue',
                        label = 'D18-Subhalo')

            ax = plt.gca()
            plt.ylabel('')
            if i == 0 and j == 0:
                plt.legend(loc='upper right')
            else:
                ax.get_legend().remove()

            if i == 0:
                ax.xaxis.set_label_position('top')
                plt.xlabel(col_labels[j])
            else:
                plt.xlabel('')
            
            if not i == nrows - 1:
                ax.set_xticklabels([])
            
            if j == 0:
                plt.text(hiptls[0].pks['k'][0], yrange[0] * 1.1,
                    'z=%.1f'%redshifts[i], fontsize = fsize, ha = 'left', va = 'bottom',
                    fontweight = 'bold')
            else:
                ax.set_yticklabels([])
        

    figsize = fig.get_size_inches()
    fig.text(border/2/figsize[0], 0.5, r'P(k) (Mpc/h)$^{-3}$',ha = 'center',
            va = 'center', fontsize=fsize)
    fig.text(0.5, border/2/figsize[1], r'k (Mpc/h)$^{-1}$', ha = 'center',
            va = 'center', fontsize=fsize)
    
    plt.savefig("HI_auto/HI_auto_pk_redshift_vs_space.png")
    plt.clf()
    return

if __name__ == '__main__':
    main()
