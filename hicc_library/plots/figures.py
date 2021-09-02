from hicc_library.plots import plot_lib as plib
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.gridspec as gspec
import sys
import os

# Helper method
def fetchKeys():
    return

def HI_auto_pk(fields, outdir, panel_length = 3, panel_bt = 0.1):
    """
    Makes two HI-auto power spectra plots, for real space and redshift space.
    Each panel represents another redshift.

    fields: list of field objects
    outdir: output directory for plots

    Dependencies: hiptl, hisubhalo, vn
    """
    
    # get info from the fields to prepare plot
    snapshots = []
    fields_for_panel = {} # organizes which fields go in which panel 
    for f in fields:
        if not f.snapshot in snapshots:
            snapshots.append(f.snapshot)
            fields_for_panel[f.shapshot] = [f]
        else:
            fields_for_panel[f.snapshot].append(f)

    # put snapshots in increasing order
    snapshots.sort()
    
    # creating figure
    npanels = len(snapshots)
    figwidth = panel_length * npanels + panel_bt * (npanels - 1)
    figheight = panel_length
    fig = plt.figure(figsize = (figwidth, figheight))

    # creating gridspec
    gs = gspec.GridSpec(1, npanels)
    plt.subplots_adjust(left = panel_bt / figwidth,
            right = 1 - panel_bt / figwidth, top = 1 - panel_bt / figwidth,
            bottom = panel_bt/figwidth, wspace = panel_bt, hspace = panel_bt)

    # now creating panels in order of increasing redshift
    panels = []
    for i in range(npanels):
        panels.append(fig.add_subplot(gs[i])

    # now making each panel
    for i in range(npanels):
        plt.sca(panels[i])
        panelf = fields_for_panel[snapshots[i]]
        for pf in panelf:
            box = pf.header['BoxSize']
            if pf.fieldname == 'vn':
                plib.plotpks(pf.pks['k'], pf.pks, box, pf.axis, pf.resolution,
                        keylist = ['vn'], colors = ['green'])
            else:
                
    return

def HI_galaxy_Xpk_methodology():
    """
    HI-galaxy cross powers separated into different panels by their methodologies.
    This plot is designed to go into the results section of the paper.

    Dependencies: hiptl, hisubhalo, vn, galaxy
    """
    return

def HI_galaxy_Xpk_color():
    """
    HI-galaxy cross powers separated into different panels by their colors.
    Made for both redshift-space and real-space.
    This plot is designed to go into the methods section of the paper.

    Dependencies: hiptl, hisubhalo, vn, galaxy
    """
    return

def color_def_sensitivity():
    return

def HI_ptl_Xpk():
    return

def dust_sensitivity():
    return

def gr_stmass():
    return

def galaxy_auto_pk():
    return

def stmass_vs_all_mass():
    return

def hiptl_nh_pk():
    return

def grid_resolution_test():
    return

def sim_resolution_test():
    return
