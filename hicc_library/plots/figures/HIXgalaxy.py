import copy
from hicc_library.plots import plot_lib as plib
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.gridspec as gspec
import numpy as np
import sys
import pickle as pkl
mpl.rcParams['text.usetex'] = True

def main():
    # remove the script name
    sys.argv.pop(0)

    # the infiles are given through the text file given in the command-line
    INFILE = sys.argv[0]
    f = open(INFILE, 'r')
    vnx = []
    hiptlx = []
    hisubx = []
    
    def name_test(fn, test):
        return test == 'galaxyX%s'%fn or test == '%sXgalaxy'%fn
    
    for p in list(f):
        p = p.replace('\n', '')
        f = pkl.load(open(p, 'rb'))
        if name_test("vn", f.fieldname):
            vnx.append(f)
        elif name_test("hiptl", f.fieldname):
            hiptlx.append(f)
        elif name_test("hisubhalo", f.fieldname):
            hisubx.append(f)
    path = '/lustre/cosinga/hcolor/figures/'
    # make the plot in real-space
    HI_galaxy_Xpk_methodology(hiptlx, hisubx, vnx)
    plt.savefig(path+"HIXgalaxy_methodology_real.png")
    plt.clf()
    # make the plot in redshift-space
    HI_galaxy_Xpk_methodology(hiptlx, hisubx, vnx, in_rss=True)
    plt.savefig(path+"HIXgalaxy_methodology_redshift.png")
    plt.clf()

    HI_galaxy_Xpk_color(hiptlx, hisubx, vnx)
    plt.savefig(path+"HIXgalaxy_color_real.png")
    plt.clf()

    HI_galaxy_Xpk_color(hiptlx, hisubx, vnx)
    plt.savefig(path+"HIXgalaxy_color_redshift.png")
    plt.clf()

    return


def HI_galaxy_Xpk_methodology(hiptls, hisubs, vns, in_rss = False, panel_length = 3, panel_bt = 0.1, border = 1,
            text_space = 0.1, fsize = 16):
    """
    HI-galaxy cross powers separated into different panels by their methodologies.
    This plot is designed to go into the results section of the paper.

    Dependencies: hiptl, hisubhalo, vn, galaxy
    """

    # get the desired keys for each field
    colors = ['red', 'blue']
    vnkeys = {}
    hiptlkeys = {}
    hisubkeys = {}
    for c in colors:
        if not in_rss:
            vnkeys[c] = plib.rmKeys(['rs'], list(vns[0].xpks.keys()))
            vnkeys[c] = plib.fetchKeys([c], vnkeys[c])
            hiptlkeys[c] = plib.rmKeys(['rs'], list(hiptls[0].xpks.keys()))
            hiptlkeys[c] = plib.fetchKeys([c], hiptlkeys[c])            
            hisubkeys[c] = plib.rmKeys(['rs'], list(hisubs[0].xpks.keys()))
            hisubkeys[c] = plib.fetchKeys([c], hisubkeys[c])
        else:
            vnkeys[c] = plib.fetchKeys(['rs', c], list(vns[0].xpks.keys()))
            hiptlkeys[c] = plib.fetchKeys(['rs', c], list(hiptls[0].xpks.keys()))
            hisubkeys[c] = plib.fetchKeys(['rs', c], list(hisubs[0].xpks.keys()))
    
    # get the yrange
    yrange = [np.inf, 0]
    fields = []
    fields.extend(hiptls)
    fields.extend(hisubs)
    fields.extend(vns)

    def contains(fn, kw):
        return kw in fn
    for f in fields:
        if contains(f.fieldname, 'hiptl'):
            keys = hiptlkeys['red']
        if contains(f.fieldname, 'hisubhalo'):
            keys = hisubkeys['red']
        if contains(f.fieldname, 'vn'):
            keys = vnkeys['red']

        for k in keys:
            pkmax = np.max(f.xpks[k])
            pkmin = np.min(f.xpks[k])
            if pkmax > yrange[1]:
                yrange[1] = pkmax
            if pkmin < yrange[0]:
                yrange[0] = pkmin
    del fields

    # get info from the fields to prepare plot
    box = hiptls[0].box
    snapshots = []
    for f in hiptls:
        if not f.field1.snapshot in snapshots:
            snapshots.append(f.field1.snapshot)
    
    # put snapshots in increasing order
    snapshots.sort()
    
    # creating figure
    nrows = len(snapshots)
    ncols = 3 # for each methodology
    figwidth = panel_length * ncols + panel_bt * (ncols - 1) + border*2
    figheight = panel_length * nrows + panel_bt * (nrows - 1) + border*2
    fig = plt.figure(figsize = (figwidth, figheight))

    # creating gridspec
    gs = gspec.GridSpec(nrows, ncols)
    plt.subplots_adjust(left = border / figwidth,
            right = 1 - border / figwidth, top = 1 - border / figwidth,
            bottom = border/figwidth, wspace = panel_bt, hspace = panel_bt)

    # now creating panels in order of increasing redshift
    panels = []
    for i in range(nrows):
        col_panels = []
        for j in range(ncols):
            col_panels.append(fig.add_subplot(gs[i,j]))
        panels.append(col_panels)
        
    
    for i in range(nrows):
        # make the hisubhalo plot for this redshift
        plt.sca(panels[i][0])
        plib.fillpks(hisubs[i].xpks['k'], hisubs[i].xpks, box, hisubs[i].field1.resolution,
                keylist = hisubkeys['blue'], color = 'blue', label = 'Blue Galaxies')

        plib.fillpks(hisubs[i].xpks['k'], hisubs[i].xpks, box, hisubs[i].field1.resolution,
                keylist = hisubkeys['red'], color = 'red', label = 'Red Galaxies')
        
        plt.ylim(yrange[0], yrange[1])
        
        # cosmetic tasks
        xts = (hisubs[i].xpks['k'][-1]-hisubs[i].xpks['k'][0])*text_space
        yts = (yrange[-1]-yrange[0])*text_space
        plt.text(hisubs[i].xpks['k'][0]+xts, yrange[0] + yts, 'z=%.1f'%snapshots[i],
                fontsize = fsize, ha = 'center', va = 'center', fontweight = 'bold')


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
        plib.fillpks(hiptls[i].xpks['k'], hiptls[i].xpks, box, hiptls[i].field1.resolution,
                keylist = hiptlkeys['blue'], color = 'blue', label = 'Blue Galaxies')

        plib.fillpks(hiptls[i].xpks['k'], hiptls[i].xpks, box, hiptls[i].field1.resolution,
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
        plib.plotpks(vns[i].xpks['k'], vns[i].xpks, box, vns[i].field1.resolution,
                keylist = vnkeys['blue'], colors = ['blue'], labels = ['Blue Galaxies'])

        plib.plotpks(vns[i].xpks['k'], vns[i].xpks, box, vns[i].field1.resolution,
                keylist = vnkeys['red'], colors = ['red'], labels = ['Red Galaxies'])
        plt.ylim(yrange[0], yrange[1])

        # cosmetic tasks
        ax = plt.gca()
        plt.ylabel('')
        ax.set_yticklabels([])
        ax.get_legend().remove()
        if i == 0:
            ax.xaxis.set_label_position('top')
            plt.xlabel('VN18-Particle', fontsize=16)
            plt.legend(loc = 'upper right')
        else:
            plt.xlabel('')
    
    fig.text(border/2/figwidth, 0.5, r'P(k)(Mpc/h)$^{-3}$', ha = 'center', va='center',
            rotation='vertical', fontsize=fsize)

    fig.text(0.5, border/2/figheight, r'k (Mpc/h)$^{-1}$', ha = 'center',
            va = 'center', fontsize=fsize)
    return

def HI_galaxy_Xpk_color(hiptls, hisubs, vns, in_rss = False, panel_length = 3, panel_bt = 0.1, text_space = 0.1,
            border = 1, fsize = 16):
    """
    HI-galaxy cross powers separated into different panels by their colors.
    Made for both redshift-space and real-space.
    This plot is designed to go into the methods section of the paper.

    Dependencies: hiptl, hisubhalo, vn, galaxy
    """
    colors = ['red', 'blue', 'resolved']
    vnkeys = {}
    hiptlkeys = {}
    hisubkeys = {}
    for c in colors:
        if not in_rss:
            vnkeys[c] = plib.rmKeys(['rs'], list(vns[0].xpks.keys()))
            vnkeys[c] = plib.fetchKeys([c], vnkeys[c])
            hiptlkeys[c] = plib.rmKeys(['rs'], list(hiptls[0].xpks.keys()))
            hiptlkeys[c] = plib.fetchKeys([c], hiptlkeys[c])            
            hisubkeys[c] = plib.rmKeys(['rs'], list(hisubs[0].xpks.keys()))
            hisubkeys[c] = plib.fetchKeys([c], hisubkeys[c])
        else:
            vnkeys[c] = plib.fetchKeys(['rs', c], list(vns[0].xpks.keys()))
            hiptlkeys[c] = plib.fetchKeys(['rs', c], list(hiptls[0].xpks.keys()))
            hisubkeys[c] = plib.fetchKeys(['rs', c], list(hisubs[0].xpks.keys()))
    print("VN keys:")
    print(vnkeys)
    print("hiptl keys:")
    print(hiptlkeys)
    print("hisubhalo keys:")
    print(hisubkeys)
    # get the yrange
    yrange = [np.inf, 0]
    fields = []
    fields.extend(hiptls)
    fields.extend(hisubs)
    fields.extend(vns)

    def contains(fn, kw):
        return kw in fn
    for f in fields:
        if contains(f.fieldname, "hiptl"):
            keys = hiptlkeys['red']
        if contains(f.fieldname, "hisubhalo"):
            keys = hisubkeys['red']
        if contains(f.fieldname, "vn"):
            keys = vnkeys['red']

        for k in keys:
            pkmax = np.max(f.xpks[k])
            pkmin = np.min(f.xpks[k])
            if pkmax > yrange[1]:
                yrange[1] = pkmax
            if pkmin < yrange[0]:
                yrange[0] = pkmin
    del fields

    # get info from the fields to prepare plot
    box = hiptls[0].box
    snapshots = []
    for f in hiptls:
        if not f.field1.snapshot in snapshots:
            snapshots.append(f.field1.snapshot)
    
    # put snapshots in increasing order
    snapshots.sort()
    
    # creating figure
    nrows = len(snapshots)
    ncols = len(colors)
    figwidth = panel_length * ncols + panel_bt * (ncols - 1) + border*2
    figheight = panel_length * nrows + panel_bt * (nrows - 1)+border*2
    fig = plt.figure(figsize = (figwidth, figheight))

    # creating gridspec
    gs = gspec.GridSpec(nrows, ncols)
    plt.subplots_adjust(left = border / figwidth,
            right = 1 - border / figwidth, top = 1 - border / figwidth,
            bottom = border/figwidth, wspace = panel_bt, hspace = panel_bt)

    # now creating panels in order of increasing redshift
    panels = []
    for i in range(nrows):
        col_panels = []
        for j in range(ncols):
            col_panels.append(fig.add_subplot(gs[i,j]))
        panels.append(col_panels)
    
    for i in range(nrows):

        # make the red plot for this redshift
        plt.sca(panels[i][0])

        plib.fillpks(hisubs[i].xpks['k'], hisubs[i].xpks, box, hisubs[i].field1.resolution,
                keylist = hisubkeys['red'], color = 'red', label = 'D18-Subhalo')
        
        plib.fillpks(hiptls[i].xpks['k'], hiptls[i].xpks, box, hiptls[i].field1.resolution,
                keylist = hiptlkeys['red'], color = 'lightcoral', label = 'D18-Particle')
        
        
        plib.plotpks(vns[i].xpks['k'], vns[i].xpks, box, vns[i].field1.resolution,
                keylist = vnkeys['red'], colors = ['darkred'], labels = ['VN18-Particle'])
        
        plt.ylim(yrange[0], yrange[1])
        
        # cosmetic tasks
        xts = (hisubs[i].xpks['k'][-1] - hisubs[i].xpks['k'][0]) * text_space
        yts = (yrange[-1] - yrange[0]) * text_space
        plt.text(hisubs[i].xpks['k'][0]+xts, yrange[0] + yts, 'z=%.1f'%snapshots[i],
                fontsize = fsize, ha = 'center', va = 'center', fontweight = 'bold')


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
        plib.fillpks(hisubs[i].xpks['k'], hisubs[i].xpks, box, hisubs[i].field1.resolution,
                keylist = hisubkeys['blue'], color = 'blue', label = 'D18-Subhalo')
        
        plib.fillpks(hiptls[i].xpks['k'], hiptls[i].xpks, box, hiptls[i].field1.resolution,
                keylist = hiptlkeys['blue'], color = 'teal', label = 'D18-Particle')


        plib.plotpks(vns[i].xpks['k'], vns[i].xpks, box, vns[i].field1.resolution,
                keylist = vnkeys['blue'], colors = ['purple'], labels = ['VN18-Particle'])
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
        plib.plotpks(vns[i].xpks['k'], vns[i].xpks, box, vns[i].field1.resolution,
                keylist = vnkeys['resolved'], colors = ['darkgreen'], labels = ['VN18-Particle'])

        plib.fillpks(hiptls[i].xpks['k'], hiptls[i].xpks, box, hiptls[i].field1.resolution,
                keylist = hiptlkeys['resolved'], color = 'palegreen', label = 'D18-Particle')

        plib.fillpks(hisubs[i].xpks['k'], hisubs[i].xpks, box, hisubs[i].field1.resolution,
                keylist = hisubkeys['resolved'], color = 'green', label = 'D18-Subhalo')
        
        plt.ylim(yrange[0], yrange[1])

        # cosmetic tasks
        ax = plt.gca()
        plt.ylabel('')
        ax.set_yticklabels([])
        ax.get_legend().remove()
        if i == 0:
            ax.xaxis.set_label_position('top')
            plt.xlabel('All-HI Cross Power', fontsize=16)
            plt.legend(loc = 'upper right')
        else:
            plt.xlabel('')
    
    fig.text(border/2/figwidth, 0.5, r'P(k)(Mpc/h)$^{-3}$', ha = 'center', va='center', 
            rotation='vertical', fontsize=fsize)

    fig.text(0.5, border/2/figheight, r'k (Mpc/h)$^{-1}$', ha = 'center',
            va = 'center', fontsize=fsize)
    return
if __name__ == '__main__':
    main()
