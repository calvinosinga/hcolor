from hc_lib.plots import plot_lib as plib
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import sys

mpl.rcParams['text.usetex'] = True

def main():
    print("loading paths...")
    OUTDIR = sys.argv.pop(1)
    paths = plib.getPaths(OUTDIR)

    print("loading pickle files...")
    gals = plib.checkPkls(paths, {'fieldname':'galaxy'})
    gdusts = plib.checkPkls(paths, {'fieldname':'galaxy_dust'})

    print("comparing ...")
    (gals, gdusts)
    return

def mass_type_and_mas(gals, gdusts, panel_length = 3, panel_bt = 0.1,
        border = 0.5, fsize=16):
    snapshots, redshifts = plib.getSnaps(gals + gdusts)
    nrows = len(snapshots)
    col_labels = ['Mass Species', 'Mass Assignment Scheme']
    
    stmass_
    return
if __name__ == '__main__':
    main()
