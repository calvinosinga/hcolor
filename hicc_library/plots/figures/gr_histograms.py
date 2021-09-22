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

    # the infiles are given through the command-line
    INFILE = sys.argv[0]
    f = open(INFILE, 'r')
    galaxy = []
    galaxy_dust = []
    for p in list(f):
        p = p.replace('\n', '')
        f = pkl.load(open(p, 'rb'))
        if f.fieldname == 'galaxy':
            galaxy.append(f)
        elif f.fieldname == 'galaxy_dust':
            galaxy_dust.append(f)
    
    gr_stmass(galaxy, galaxy_dust)

    # save the plot
    plt.savefig("/lustre/cosinga/hcolor/figures/gr_stmass.png")
    plt.clf()
    # now make just gr histogram
    gr_hist(galaxy, galaxy_dust)
    plt.savefig("/lustre/cosinga/hcolor/figures/gr_hist.png")

    return

def gr_stmass(galaxy, galaxy_dust, panel_length = 8, panel_bt = 0.25, 
            border = 1, cbar_width = 1, text_space = 0.1, fsize = 24):
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
        
        red_colors = ['darkred', 'firebrick', 'red', 'salmon', 'lightsalmon', 'mistyrose']

        x = np.linspace(xlim[0], xlim[1])

        # we want the higher lines to be more red
        vbs = []
        for k,v in col_defs.items():
            vbs.append(v['b'])
        vbs.sort()
        for k,v in col_defs.items():
            if v['m'] == 0:
                label = "%.2f"%v['b']
            else:
                label = "%.2f + %.2f(log($M_*$) - %.2f)"%(v['b'], v['m'], abs(v['mb']))
            idx = vbs.index(v['b'])
            v['color'] = red_colors[-1*idx]
            funcs[label] = v


        plt.sca(panels[row_idx][col_idx])
        if nlim[0] <= 0:
            nlim[0] = 1
        plt.imshow(np.rot90(plot_field.gr_stmass[0]), norm=mpl.colors.LogNorm(vmin=nlim[0], vmax=nlim[1]), 
                extent=(xlim[0], xlim[1], ylim[0], ylim[1]))
        
        def gr_lines(x, b, m, mb):
            return b + m*(x+mb)
        
        for fkey, ft in funcs.items():
            plt.plot(x, gr_lines(x, ft['b'], ft['m'], ft['mb']), label=fkey, color=ft['color'])

        
        ax = plt.gca()
        ax.xaxis.set_label_position('top')
        ax.set_aspect('auto')

        plt.legend(loc = 'lower right', prop = {'size':fsize/2})
        if col_idx == 0:
            xts = (xlim[1]-xlim[0]) * text_space
            yts = (ylim[1]-ylim[0]) * text_space
            plt.text(xlim[1]-xts, ylim[0]+yts, '$z$=%.1f'%plot_field.header['Redshift'], 
                    fontsize=fsize, ha = 'center', va = 'center', fontweight = 'bold')
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
    lab_border = border*1.5 # borders with labels and ticks need extra space

    ncols = panel_length*nhist + cbar_width
    # create the figure with the right dimensions
    figwidth = panel_length * nhist + panel_bt * (nhist - 1) + cbar_width + lab_border*2
    # one label border for y-axis, another for colorbar
    figheight = panel_length * nrows + panel_bt * (nrows - 1) + lab_border + border
    fig = plt.figure(figsize = (figwidth, figheight))

    # creating gridspec
    gs = gspec.GridSpec(nrows, ncols)
    plt.subplots_adjust(left = lab_border / figwidth,
            right = 1 - border / figwidth, top = 1 - border / figwidth,
            bottom = lab_border/figwidth, wspace = panel_bt, hspace = panel_bt)

    panels = []
    for i in range(nrows):
        col_panels = []
        for j in range(nhist):
            col_panels.append(fig.add_subplot(gs[i, panel_length*j:panel_length*(j+1)]))
        col_panels.append(fig.add_subplot(gs[i, panel_length*nhist:panel_length*nhist+cbar_width]))
        panels.append(col_panels)


    tick_font_size = 0.75*fsize
    for i in range(nrows):
        if galaxy:
            make_panel(galaxy, i)
            ax = plt.gca()
            ax.tick_params(axis="both", direction="in")
            plt.yticks(fontsize=tick_font_size)
            if i==0:
                plt.xlabel('No Dust', fontsize = fsize)
                plt.xticks(fontsize=tick_font_size)
            else:
                ax.get_legend().remove()
                ax.set_xticklabels([])
                

        
        if galaxy_dust:
            make_panel(galaxy_dust, i)
            ax = plt.gca()
            if i == 0:
                plt.xlabel('Dust-Attenuated', fontsize = fsize)
                plt.xticks(fontsize=tick_font_size)
            else:
                ax.set_xticklabels([])
            ax.set_yticklabels([])
            ax.get_legend().remove()
            ax.tick_params(axis="both", direction="in")
        


        plt.sca(panels[i][nhist])
        ax = plt.gca()
        plt.colorbar(cax=ax)
        plt.ylabel("$N_g$ (count)", fontsize = fsize)
        plt.yticks(fontsize=tick_font_size)
    fig.text(0.5, lab_border/2/figheight, r'log($M_{*}$)', ha = 'center', va = 'center', fontsize=fsize)
    fig.text(lab_border/2/figwidth, 0.5, 'g-r (magnitude)', va='center', ha = 'center', rotation = 'vertical',
               fontsize = fsize)
    return

def gr_hist(galaxy, galaxy_dust, panel_length = 3, panel_bt = 0.1, text_space = 0.1, border = 0.5, 
                color_thresh = 0.65):
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
        
        if fields[0].fieldname == 'galaxy' or ncols == 1:
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
        rgb[:, 0] = 1.25 / (x[-1] - color_thresh) * (x - color_thresh) + 0.35
        rgb[:, 2] = 0.85 / (x[0] - color_thresh) * (x - color_thresh)
        
        rgb = np.where(rgb < 1, rgb, np.ones(rgb.shape))
        rgb = np.where(rgb > 0, rgb, np.zeros(rgb.shape))

        plt.sca(panels[row_idx][col_idx])
        
        plt.bar(x, hist, width = x[1] - x[0], color=rgb)
        plt.ylim(ylim[0], ylim[1])
        plt.xlim(xlim[0], xlim[1])

        ax = plt.gca()
        ax.tick_params(axis = 'both', direction = 'in')

        if col_idx == 0:
            xts = (xlim[1]-xlim[0])*text_space
            yts = (ylim[1]-ylim[0])*text_space
            plt.text(xlim[0]+xts, ylim[1]-yts, '$z$=%.1f'%plot_field.header['Redshift'], 
                fontsize=16, ha = 'left', va = 'top', fontweight = 'bold')
        else:
            ax.set_yticklabels([])

        return

    #########################################################################################################

        
    xlim = [np.inf, 0]
    ylim = [np.inf, 0]
    snapshots = []

    get_plot_lims(galaxy)
    get_plot_lims(galaxy_dust)
    
    snapshots.sort()

    nrows = len(snapshots)
    ncols = 0
    if galaxy:
        ncols += 1
    if galaxy_dust:
        ncols += 1
    top_border = border
    bot_border = border*2
    figwidth = panel_length * ncols + panel_bt * (ncols - 1) + border*2
    figheight = panel_length * nrows + panel_bt * (nrows - 1) + bot_border + top_border
    fig = plt.figure(figsize = (figwidth, figheight))

    # creating gridspec
    gs = gspec.GridSpec(nrows, ncols)
    plt.subplots_adjust(left = border / figwidth,
            right = 1 - border / figwidth, top = 1 - top_border / figwidth,
            bottom = bot_border/figwidth, wspace = panel_bt, hspace = panel_bt)

    panels = []
    for i in range(nrows):
        col_panels = []
        for j in range(ncols):
            col_panels.append(fig.add_subplot(gs[i, j]))
        panels.append(col_panels)
    
    for i in range(nrows):
        if galaxy:
            make_panel(galaxy, i)
            ax = plt.gca()
            ax.xaxis.set_label_position('top')
            plt.xlabel("No Dust", fontsize=16)

        if galaxy_dust:
            make_panel(galaxy_dust, i)
            ax = plt.gca()
            ax.xaxis.set_label_position('top')
            plt.xlabel("Dust-Attenuated", fontsize=16)
    
    fig.text(0.5, border/2/figheight, 'g-r (magnitude)', va = 'center', 
                ha = 'center', fontsize=16)
    fig.text(1-border/2/figwidth, 0.5, '$N_g$ (count)', va = 'center', 
                ha = 'center', rotation = 'vertical', fontsize = 16)
    return


if __name__ == '__main__':
    main()
