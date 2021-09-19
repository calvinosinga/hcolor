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
    plt.savefig("/lustre/cosinga/gr_stmass.png")

    # now make just gr histogram

    #gr_hist(galaxy, galaxy_dust)
    #plt.savefig("/lustre/cosinga/gr_hist.png")
    return

def gr_stmass(galaxy, galaxy_dust, panel_length = 8, panel_bt = 0.1, cbar_width = 1, text_space = 0.1):
    ############ HELPER METHOD ##########################################
    def get_snap_lims(fields):
        
        for f in fields:
            if f.snapshot not in snapshots:
                snapshots.append(f.snapshot)
            xlim[0] = min(np.min(f.gr_stmass[1]), xlim[0])
            xlim[1] = max(np.max(f.gr_stmass[1]), xlim[1])
            ylim[0] = min(np.min(f.gr_stmass[2]), ylim[0])
            ylim[1] = max(np.max(f.gr_stmass[2]), ylim[1])
            nlim[0] = min(np.min(f.gr_stmass[0]), nlim[0])
            nlim[1] = max(np.max(f.gr_stmass[0]), nlim[1])
        return
    
    def make_panel(fields, row_idx):
        
        if fields[row_idx].fieldname == 'galaxy' or nhist == 1:
            col_idx = 0
        else:
            col_idx = 1
        plot_field = None
        for f in fields:
            if f.snapshot == snapshots[row_idx]:
                plot_field = f

        if plot_field is None:
            return
        
        # functions for the color cuts
        col_defs = plot_field.getColorDefinitions()
        funcs = {}
        
        x = np.linspace(xlim[0], xlim[1])
        for k,v in col_defs.items():
            if v['m'] == 0:
                label = "$%.2f$"%v['b']
            else:
                label = "$%.2f + %.2f(log(M_*) - %.2f)$"%(v['b'], v['m'], v['mb'])
            funcs[label] = lambda st_mass: v['b'] + (v['m'] * st_mass + v['mb'])

        plt.sca(panels[row_idx][col_idx])
        if nlim[0] <= 0:
            nlim[0] = 1e-4
        plt.imshow(np.rot90(plot_field.gr_stmass[0]), norm=mpl.colors.LogNorm(vmin=nlim[0], vmax=nlim[1]), 
                extent=(xlim[0], xlim[1], ylim[0], ylim[1]))
        
        for k, fntn in funcs.items():
            plt.plot(x, fntn(x), label=k)

        
        ax = plt.gca()
        ax.xaxis.set_label_position('top')
        

        plt.legend(loc = 'upper right')
        if col_idx == 0:
            plt.text(xlim[1]-text_space, ylim[0]+text_space, 'z=%.1f'%plot_field.header['Redshift'], 
                    fontsize=16, ha = 'right', va = 'bottom', fontweight = 'bold')
        return
    ########################################################################
    snapshots = []
    xlim = [np.inf, 0]
    ylim = [np.inf, 0]
    nlim = [np.inf, 0]
    get_snap_lims(galaxy)
    get_snap_lims(galaxy_dust)
    snapshots.sort()

    nhist = 0
    if galaxy:
        nhist += 1
    if galaxy_dust:
        nhist += 1
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
        col_panels.append(fig.add_subplot(gs[i, panel_length*nhist:panel_length*nhist+cbar_width]))
        panels.append(col_panels)



    for i in range(nrows):
        if galaxy:
            make_panel(galaxy, i)
            ax = plt.gca()
            ax.tick_params(axis="both", direction="in")
            if i==0:
                plt.xlabel('No Dust', fontsize = 16)
            else:
                ax.get_legend().remove()
            

        
        if galaxy_dust:
            make_panel(galaxy_dust, i)
            ax = plt.gca()
            if i == 0:
                plt.xlabel('Dust-Attenuated', fontsize = 16)
            else:
                ax.get_legend().remove()
            ax.set_yticklabels([])
            ax.tick_params(axis="both", direction="in")
        


        plt.sca(panels[i][nhist+1])
        ax = plt.gca()
        plt.colorbar(cax=ax)
        plt.ylabel("$N_g (count)$")
    fig.text(0.45, -.075, r'log($M_{*}$)', va = 'center', fontsize=16)
    fig.text(-0.075, 0.45, 'g-r (magnitude)', ha = 'center', rotation = 'vertical',
                fontsize = 16)
    plt.title("Color-Stellar Mass")

def gr_hist(galaxy, galaxy_dust, panel_length = 3, panel_bt = 0.1, text_space = 0.1, color_thresh = 0.65):
    ######################### HELPER METHOD ###############################################################
    def get_plot_lims(fields):
        
        for f in fields:
            if f.snapshot not in snapshots:
                snapshots.append(f.snapshot)
            mid, hist = get_hist(f.gr_stmass)
            xlim[0] = min(np.min(mid), xlim[0])
            xlim[1] = max(np.max(mid), xlim[1])
            ylim[0] = min(np.min(hist), ylim[0])
            ylim[1] = max(np.max(hist), ylim[1])
        return
            
    def get_hist(gr):
        mid = []
        for i in range(len(gr[2])-1):
            mid.append((gr[2][i] + gr[2][i+1]) / 2)
        hist = np.sum(gr[0], axis=0)
        return np.array(mid), hist

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
        
        x, hist = get_hist(plot_field.gr_stmass)
        
        rgb = np.zeros((x.shape[0],3))
        rgb[:, 0] = 1.1 / (x[-1] - color_thresh) * (x - color_thresh)
        rgb[:, 2] = 0.85 / (x[0] - color_thresh) * (x - color_thresh)



        plt.sca(panels[row_idx][col_idx])
        
        plt.bar(x, hist, width = x[1] - x[0], color=rgb)
        plt.ylim(ylim[0], ylim[1])
        plt.xlim(xlim[0], xlim[1])
        return

    #########################################################################################################

        
    xlim = [np.inf, 0]
    ylim = [np.inf, 0]
    snapshots = []

    get_plot_lims(galaxy)
    get_plot_lims(galaxy_dust)
    ncols = 2

    figwidth = panel_length * ncols + panel_bt * (ncols - 1)
    figheight = panel_length * nrows + panel_bt * (nrows - 1)
    fig = plt.figure(figsize = (figwidth, figheight))

    gs = gspec.GridSpec(nrows, ncols)


if __name__ == '__main__':
    main()
