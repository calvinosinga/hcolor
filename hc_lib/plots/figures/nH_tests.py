from hc_lib.plots import plot_lib as plib
import h5py as hp
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.gridspec as gspec
import pickle as pkl
import numpy as np
import sys

mpl.rcParams['text.usetex'] = True

def main():
    sys.argv.pop(0)
    OUTDIR = sys.argv.pop(0)
    INGRIDS = sys.argv
    paths = plib.getPaths(OUTDIR)
    nhs = plib.checkPkls(paths, {'fieldname':"hiptl_nH"})
    grids = []
    for i in INGRIDS:
        grids.append(hp.File(i, 'r'))
#    vel_mass_hist(nhs, grids, 3, 0.1, 0.5, 16)
#    plt.savefig("nh_vel_mass_hist.png")
    # plot that puts each nH bin on its own panel, compare redshift space to real space
    redshift_model(nhs, grids, 3, 0.1, 0.5, 16)
    redshift_nHbin(nhs, grids, 3, 0.1, 0.5, 16)
    plt.savefig("nh_redshift_vs_real_space.png")

    # plot that puts all nH bins on same 

    return

def vel_mass_hist(nhs, gridfiles, panel_length, panel_bt, border, fsize):

    # get nlimits
    def get_nlim(gridfile, nh_bins):
        nlim = [np.inf, 0]
        for i in range(len(nh_bins)):
            key = str(nh_bins[i])
            hist = gridfile[key]
            hmin = np.min(hist)
            hmax = np.max(hist)
            if nlim[0] > hmin:
                nlim[0] = hmin
            if nlim[1] < hmax:
                nlim[1] = hmax
        return nlim

            
    # TODO: probably should make some check to order both nhs, gridfiles lists
    nrows = len(gridfiles)
    ncols = len(nhs[0].getnHBinStrings())
    fig, panels = plib.createFig(panel_length, nrows, ncols, panel_bt, border, border)
    for i in range(nrows):
        # getting bin info for this nh
        nh = nhs[i]
        grid = gridfiles[i]
        nh_bin_names = nh.getnHBinStrings()
        velocity_bins = nh.vel_bins
        mass_bins = nh.m_bins

        nlim = get_nlim(grid, nh_bin_names)
        for j in range(ncols):
            plt.sca(panels[i][j])
            
            key = str(nh_bins[j])
            hist = grid[key]
            plt.imshow(np.rot90(hist), norm=mpl.colors.LogNorm(vmin=nlim[0], vmax=nlim[1]),
                extent=(mass_bins[0], mass_bins[-1], velocity_bins[0], velocity_bins[-1]))

    figsize = fig.get_size_inches()
    fig.text(0.5, border/2/figsize[1], r'gas cell mass (M$_\odot$)',
            ha = 'center', va='center', fontsize = fsize)
    
    fig.text(border/2/figsize[0], 0.5, r'line-of-sight velocity (km/s)',
            ha='center', va='center', fontsize = fsize)

    return

def redshift_model(nhs, gridfiles, panel_length, panel_bt, border, fsize):
    nrows = len(nhs)
    ncols = len(nhs[0]

if __name__ == '__main__':
    main()
