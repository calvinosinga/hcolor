import pickle as pkl
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.gridspec as gspec
import sys
import os

GDPATH = sys.argv[1]
PLOTDIR = sys.argv[2]

gd = pkl.load(open(GDPATH, 'rb'))

def HI_auto_pk():
    """
    Makes two HI-auto power spectra plots, for real space and redshift space.

    Dependencies: hiptl, hisubhalo, vn
    """

    return

def HI_cross_pk_methodology():
    """
    HI-galaxy cross powers separated into different panels by their methodologies.
    This plot is designed to go into the results section of the paper.

    Dependencies: hiptl, hisubhalo, vn, galaxy
    """
    return

def HI_cross_pk_color():
    """
    HI-galaxy cross powers separated into different panels by their colors.
    This plot is designed to go into the methods section of the paper.

    Dependencies: hiptl, hisubhalo, vn, galaxy
    """
    return

def color_def_sensitivity():
    return

def dust_sensitivity():
    return

def gr_stmass():
    return

def galaxy_auto_pk():
    return
