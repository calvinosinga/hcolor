from hicc_library.plots import plot_lib as plib
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.gridspec as gspec
import copy
import numpy as np
import sys

mpl.rcParams['text.usetex'] = True

# remove the script name
sys.argv.pop(0)

# the infiles are given through the command-line
INPKLS = sys.argv

