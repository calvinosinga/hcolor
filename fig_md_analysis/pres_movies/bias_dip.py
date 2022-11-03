import pkfire.dist_lib.dist as dlib
from pkfire.ptl_lib.particle import Particles
from pkfire.pkfire import Pkfire, XPkfire
from pkfire.grid_lib.grid import Grid
from pkfire.movie_lib.movie_super import Movie
import numpy as np
import matplotlib.pyplot as plt

#### INPUTS

num_sigma = 10
nnodes = 100
nframes = 10
make_movie = False
####

def plot(pkf):
    ncols = 4
    wspace = 0.5
    wrs = np.ones(ncols)
    wrs[-1] = 0.15
    fig, axes = Movie._makeFig(ncols, width_ratios = wrs, gspec_kw = {'wspace':wspace})
    
    pkf.pkPlot(axes[0])
    pkf.obsbiasPlot(axes[1])
    stpkf.ptlPlot(axes[2], axes[3])
    
    axes[0].set_ylabel('P (k) (h / cMpc)$^3$', fontsize = 12)
    axes[1].set_ylabel('b (k)')
    axes[2].set_xlabel('x (cMpc / h)')
    axes[2].set_ylabel('y (cMpc / h)')
    axes[3].set_ylabel('M (M$_\\odot$)')
    fig.text(0.5, 0, 'k (h / cMpc)', fontsize = 12, ha = 'center', va = 'bottom')
    for ax in axes:
        ax.tick_params(direction = 'in')
    
    ybias = axes[1].get_ylim()
    if ybias[1] - ybias[0] < 1:
        axes[1].set_ylim([0.5, 1.5])
    return fig, axes


tngpath = '/home/cosinga/scratch/L75n1820TNG/output/'
savepath = '/home/cosinga/scratch/hcolor/fig_md_analysis/pres_movies/'
il = dlib.Illustris('/Users/cosinga/illustris/L75n1820TNG/output/', 99)

mask = il.maskMass(mass_min = 2e8)
print("number of galaxies: %d"%np.sum(mask))
mass = il.getMass()
himass = np.copy(mass) * 0.1
pos = il.getPos()

grpmass = il.getGroupMass()
gmass_mean = np.mean(grpmass)
gmass_stdev = np.std(grpmass)
gmass_min = gmass_mean + gmass_stdev * num_sigma
top_gmass_mask = il.maskGroupMass(mass_min = gmass_min)
gmass_idx_list = np.where(top_gmass_mask)[0]
print('number of halos getting their HI reduced: %d'%len(gmass_idx_list))
gmass_sub_mask = np.zeros_like(mask, dtype = bool)

for idx in gmass_idx_list:
    haloid_mask = il.maskHalo(idx)
    gmass_sub_mask = gmass_sub_mask | haloid_mask

gmass_sub_mask = gmass_sub_mask & mask


pkflist = []
gridshape = [nnodes]*3

gals_stmass = Particles(pos, mass)
stgrid = Grid(gridshape, il.getBox())
stpkf = Pkfire(stgrid, gals_stmass)



if make_movie:
    for i in range(nframes):
        gals_hi = Particles(pos, himass)
        higrid = Grid(gridshape, il.getBox())
        hipkf = Pkfire(higrid, gals_hi)

        xpkf = XPkfire(stpkf, hipkf)
        pkflist.append(xpkf)

else:
    gals_hi = Particles(pos, himass)
    higrid = Grid(gridshape, il.getBox())
    hipkf = Pkfire(higrid, gals_hi)

    xpkf = XPkfire(stpkf, hipkf)
    fig, axes = plot(xpkf)
    fig.savefig(savepath + 'test.png')
