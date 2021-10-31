from hc_lib.plots import plot_lib as plib
import h5py as hp
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.gridspec as gspec
import copy
import pickle as pkl
import numpy as np
import sys

mpl.rcParams['text.usetex'] = True

def main():
    sys.argv.pop(0)
    INFILE = sys.argv.pop(1)
    INGRID = sys.argv.pop(2)
    nh = pkl.load(open(INFILE, 'rb'))
    grid = hp.File(INGRID, 'r')
    vel_mass_hist(nh, grid)
    return

def vel_mass_hist(nh, gridfile):
    velocity_bins = nh.vel_bins
    mass_bins = nh.m_bins
    nh_bins = nh._getnHBins

    fig, panels = plib.createFig(3, 1, len(nh_bins), 0.1, 0.5, 0.5)
    for i in range(len(nh_bins)):
        

    return


if __name__ == '__main__':
    main()