from hicc_library.plots import plot_lib as plib
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.gridspec as gspec
import copy
import numpy as np
import sys
import pickle as pkl
mpl.rcParams['text.usetex'] = True

def main():

    # remove the script name
    sys.argv.pop(0)

    # the infiles are given through the command-line
    INPKLS = sys.argv
    galaxy = []
    galaxy_dust = []
    for p in INPKLS:
        f = pkl.load(open(p, 'rb'))
        if f.fieldname == 'galaxy':
            galaxy.append(f)
        elif f.fielname == 'galaxy_dust':
            galaxy_dust.append(f)
    
    gr_stmass(galaxy, galaxy_dust)

    # save the plot

    # now make just gr histogram
    return

def gr_stmass(galaxy, galaxy_dust, panel_length = 8, panel_bt = 0.1, cbar_width = 1):
    ############ HELPER METHOD ##########################################
    def get_snap_lims(fields):
        
        for f in fields:
            if f.snapshot not in snapshots:
                snapshots.append(f.snapshot)
            xlim[0] = min(np.min(f.gr_stmass[1]), xlim[0])
            xlim[1] = max(np.max(f.gr_stmass[1]), xlim[1])
            ylim[0] = min(np.min(f.gr_stmass[1]), ylim[0])
            ylim[1] = max(np.max(f.gr_stmass[1]), ylim[1])
        return
    
    def make_panel(fields, row_idx):
        if fields[0].fieldname == 'galaxy':
            col_idx = 0
        else:
            col_idx = 1
        plot_field = None
        for f in fields:
            if f.snapshot == snapshots[row_idx]:
                plot_field = f

        if plot_field is None:
            return
        
        plt.sca(panels[row_idx][col_idx])
        
        plt.imshow(np.rot90(plot_field.gr[0]), norm=mpl.colors.LogNorm(), 
                extent=(xlim[0], xlim[1], ylim[0], ylim[1]))

        for k,v in funcs.items():
            plt.plot(x, v(x), label=k)

        
        ax = plt.gca()
        ax.xaxis.set_label_position('top')
        plt.ylim(ylim[0], ylim[1])
        plt.xlim(xlim[0], xlim[1])

        plt.legend()
        return
    ########################################################################
    
    snapshots = []
    xlim = [np.inf, 0]
    ylim = [np.inf, 0]

    get_snap_lims(galaxy)
    get_snap_lims(galaxy_dust)
    snapshots.sort()
    
    
    nhist = 2
    nrows = len(snapshots)

    # making the gr-stellar mass plot

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
    for i in range(nrows):
        col_panels = []
        for j in range(nhist):
            col_panels.append(fig.add_subplot(gs[i, panel_length*j:panel_length*(j+1)]))
        col_panels.append(fig.add_subplot(gs[i, panel_length*2:panel_length*2+cbar_width]))
        panels.append(col_panels)

    # functions for the color cuts
    col_defs = galaxy.getColorDefinitions()
    funcs = {}
    x = np.linspace(xlim[0], xlim[1])
    for k,v in col_defs.items():
        funcs[k] = lambda x: v['b'] + (v['m'] * x + v['mb'])

    for i in range(nrows):

        make_panel(galaxy, i)
        plt.xlabel('No Dust', fontsize = 16)

        make_panel(galaxy_dust, i)

        plt.xlabel('Dust-Attenuated', fontsize = 16)
        ax.set_yticklabels([])
        for k,v in funcs.items():
            plt.plot(x, v(x), label=k)

        plt.sca(panels[2])
        ax = plt.gca()
        plt.colorbar(cax=ax)
        fig.text(0.45, -.075, r'log($M_{*}$)', va = 'center', fontsize=16)
        fig.text(-0.'g-r (magnitude)')
        plt.title("Color-Stellar Mass for z=%.1f"%galaxy.snapshot)

if __name__ == '__main__':
    main()