import copy
from hc_lib.plots import plot_lib as plib
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
    
    def name_test(fn, test):
        return test == fn
    
    for p in list(f):
        p = p.replace('\n', '')
        f = pkl.load(open(p, 'rb'))
        if name_test("galaxy", f.fieldname):
            galaxy.append(f)
        elif name_test("galaxy_dust", f.fieldname):
            galaxy_dust.append(f)
    
    path = '/lustre/cosinga/hcolor/figures/'
    galaxy_auto(galaxy, galaxy_dust)
    plt.savefig(path+"galaxy_auto_gr_sensitivity_real.png")
    plt.clf()

    galaxy_auto(galaxy, galaxy_dust, in_rss=True)
    plt.savefig(path+"galaxy_auto_gr_sensitivity_redshift.png")
    plt.clf()

    HIXgalaxy
    return

# two columns for galaxy and galaxy_dust
# a row for each snapshot

def galaxy_auto(galaxy, galaxy_dust, in_rss = False, panel_length = 3, 
            panel_bt = 0.1, text_space=0.1, border = 1):
    
    return

# columns for red/blue/all, rows for snapshots
def HIXgalaxy():
    return
if __name__ == '__main__':
    main()