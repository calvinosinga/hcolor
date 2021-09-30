from hicc_library.plots import plot_lib as plib
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.gridspec as gspec
import copy
import pickle as pkl
import numpy as np
import sys

mpl.rcParams['text.usetex'] = True

def main():
    # remove the script name
    sys.argv.pop(0)

    # the infiles are given through the command-line
    INFILE = sys.argv[0]
    f = open(INFILE, 'r')
    vn = []
    hiptl = []
    hisub = []
    
    def name_test(fn, test):
        return test == fn
    
    for p in list(f):
        p = p.replace('\n', '')
        f = pkl.load(open(p, 'rb'))
        if name_test("vn", f.fieldname):
            vn.append(f)
        elif name_test("hiptl", f.fieldname):
            hiptl.append(f)
        elif name_test("hisubhalo", f.fieldname):
            hisub.append(f)
    path = '/lustre/cosinga/hcolor/figures/'
    HI_auto_pk(hiptl, hisub, vn)
    plt.savefig(path+"HI_auto_real.png")
    plt.clf()

    HI_auto_pk(hiptl, hisub, vn, in_rss=True)
    plt.savefig(path+"HI_auto_redshift.png")
    plt.clf()
    return


def HI_auto_pk(hiptls, hisubs, vns, in_rss = False, panel_length = 3, 
            panel_bt = 0.1, text_space=0.1, border = 1):
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
    # get the yrange
    print(hiptlkeys)
    print(hisubkeys)
    print(vnkeys)
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
        pklen = len(f.pks['k'][:])
        for k in keys:
            pkmax = np.max(f.pks[k])
            pkmin = np.min(f.pks[k])
            if pkmax > yrange[1]:
                yrange[1] = pkmax
            if pkmin < yrange[0]:
                yrange[0] = pkmin
            if not len(f.pks[k]) == pklen:
                print(k)
    del fields

    # get info from the fields to prepare plot

    snapshots = []
    for f in hiptls:
        if not f.snapshot in snapshots:
            snapshots.append(f.snapshot)
    
    # put snapshots in increasing order
    snapshots.sort()
    
    # creating figure
    npanels = len(snapshots)
    figwidth = panel_length * npanels + panel_bt * (npanels - 1) + border * 2
    figheight = panel_length + border * 2
    fig = plt.figure(figsize = (figwidth, figheight))

    # creating gridspec
    gs = gspec.GridSpec(1, npanels)
    plt.subplots_adjust(left = border / figwidth,
            right = 1 - border / figwidth, top = 1 - border / figwidth,
            bottom = border/figwidth, wspace = panel_bt, hspace = panel_bt)

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
            plt.ylabel('')
            ax.get_legend().remove()
        else:
            plt.legend(loc = 'upper right')
        plt.ylim(yrange[0], yrange[1])
        
        # output textbox onto the plot with redshift
        plt.text(hiptls[0].pks['k'][0] + text_space, yrange[0] + text_space,
                'z=%.1f'%snapshots[i], fontsize = 20, ha = 'center', va = 'center',
                fontweight = 'bold') 

    return
if __name__ == '__main__':
    main()
