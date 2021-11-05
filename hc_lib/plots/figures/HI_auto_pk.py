
from hc_lib.plots import plot_lib as plib
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.gridspec as gspec
import copy
import pickle as pkl
import numpy as np
import sys

mpl.rcParams['text.usetex'] = True

def main():
    
    
    # def name_test(fn, test):
    #     return test == fn
    
    # for p in list(f):
    #     p = p.replace('\n', '')
    #     f = pkl.load(open(p, 'rb'))
    #     if name_test("vn", f.fieldname):
    #         vn.append(f)
    #     elif name_test("hiptl", f.fieldname):
    #         hiptl.append(f)
    #     elif name_test("hisubhalo", f.fieldname):
    #         hisub.append(f)
    # path = '/lustre/cosinga/hcolor/figures/'
    # HI_auto_pk(hiptl, hisub, vn)
    # plt.savefig(path+"HI_auto_real.png")
    # plt.clf()

    # HI_auto_pk(hiptl, hisub, vn, in_rss=True)
    # plt.savefig(path+"HI_auto_redshift.png")
    # plt.clf()
    return




def HI_auto_pk(hiptls, hisubs, vns, in_rss = False, panel_length = 3, 
            panel_bt = 0.1, text_space=0.9, border = 0.5, fsize=16):
    """
    Makes HI-auto power spectra plots, for real space or redshift space.
    Each panel represents another redshift.

    hiptls: list of hiptl objects
    hisubs: list of hisubhalo objects
    vns: list of vn objects
    """

    # get the desired keys for each field - if the fields are not
    # in the results, then make the keys an empty list
    if not in_rss:
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
    else:
        if vns:
            vnkeys = ['vnrs']
        else:
            vnkeys = []
        if hiptls:
            hiptlkeys = plib.fetchKeys(['rs'], list(hiptls[0].pks.keys()))
        else:
            hiptlkeys = []
        if hisubs:
            hisubkeys = plib.fetchKeys(['rs'], list(hisubs[0].pks.keys()))
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
