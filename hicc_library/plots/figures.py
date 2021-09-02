from hicc_library.plots import plot_lib as plib
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.gridspec as gspec
import sys
import os
import copy

# Helper method
def _fetchKeys(keyword, keylist, exclude = False):
    res = []
    for k in keylist:
        if keyword in k and not exclude:
            res.append(k)
        elif not keyword in k and exclude:
            res.append(k)
    return res

def _rmKeys(keywords, keylist):
    klist = copy.copy(keylist)
    for word in keywords:
        for k in klist:
            if word in k:
                klist.remove(k)
    return klist


def HI_auto_pk(fields, outpath, panel_length = 3, panel_bt = 0.1, yrange = (1, 1e4),
        text_space=0.1):
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
        panels.append(fig.add_subplot(gs[i]))

    # now making each panel
    for i in range(npanels):
        plt.sca(panels[i])
        panelf = fields_for_panel[snapshots[i]]
        for pf in panelf:
            # plotting the pk
            keylist = list(pf.pks.keys())
            box = pf.header['BoxSize']
            if pf.fieldname == 'vn':
                plib.plotpks(pf.pks['k'], pf.pks, box, pf.axis, pf.resolution,
                        keylist = ['vn'], colors = ['green'],
                        labels = ['V-N18'])
            if pf.fieldname == 'hiptl':
                pkeys = _rmKeys(['rs','k'], keylist)
                plib.fillpks(pf.pks['k'], pf.pks, box, pf.axis, pf.resolution,
                        keylist = pkeys, color = 'blue', label = 'D18-particle')
            if pf.fieldname == 'hisubhalo':
                pkeys = _rmKeys(['rs','k'], keylist)
                plib.fillpks(pf.pks['k'], pf.pks, box, pf.axis, pf.resolution,
                        keylist = pkeys, color = 'orange', label = 'D18-subhalo')
            
            # cosmetic tasks
            if not i == 0:
                ax = plt.gca()
                ax.set_yticklabels([])
                plt.ylabel('')
                ax.get_legend().remove()
            plt.ylim(yrange[0], yrange[1])
        
        # output textbox onto the plot with redshift
        plt.text(panelf[0].pks['k'] + text_space, yrange[0] + text_space,
                'z=%.1f'%snapshots[i], fontsize = 20, ha = 'left', va = 'bottom',
                fontweight = 'bold', 

    # save the plot
    f = fields[0]
    plotname = 'HI_auto_real_%sB_%03dS_%dA_%dR'%(f.simname, f.snapshot, f.axis,
            f.resolution)
    plt.savefig(outpath+plotname+'.png')
    plt.clf()

    # now do the same for the redshift space plot

    # now split them into different panels according to methodology
    return

def HI_galaxy_Xpk_methodology(fields, outpath, panel_length = 3, panel_bt = 0.1, yrange =()):
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
