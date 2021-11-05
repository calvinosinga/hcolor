
from hc_lib.plots import plot_lib as plib
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.gridspec as gspec
import copy
import pickle as pkl
import numpy as np
import sys

mpl.rcParams['text.usetex'] = True

def main():
    # remove the script name
    sys.argv.pop(0)

    OUTDIR = sys.argv[0]
    paths = plib.getPaths(OUTDIR)
       
    h2ptls = plib.checkPkls(paths, {'fieldname':'h2ptl'})
    hiptls = plib.checkPkls(paths, {'fieldname':'hiptl'})
    vns = plib.checkPkls(paths, {'fieldname':'vn'})
    
    make_ptl_slices(hiptls, h2ptls, vns)

    hisubs = plib.checkPkls(paths, {'fieldname':'hisubhalo'})

    #compare_HI_slices(hiptls, vns, hisubs)
    
    # def name_test(fn, test):
    #     return test == fn
    
    # for p in list(f):
    #     p = p.replace('\n', '')
    #     f = pkl.load(open(p, 'rb'))
    #     if name_test("vn", f.fieldname):
    #         vn.append(f)
    #     elif name_test("hiptl", f.fieldname):
    #         hiptl.append(f)
    #     elif name_test("hisubhalo", f.fieldname):
    #         hisub.append(f)
    # path = '/lustre/cosinga/hcolor/figures/'
    # HI_auto_pk(hiptl, hisub, vn)
    # plt.savefig(path+"HI_auto_real.png")
    # plt.clf()

    # HI_auto_pk(hiptl, hisub, vn, in_rss=True)
    # plt.savefig(path+"HI_auto_redshift.png")
    # plt.clf()
    return

def make_ptl_slices(hiptls, h2ptls, vns, panel_length = 3,
            panel_bt = 0.1, border = 0.5):
    for i in range(len(hiptls)):
        h = hiptls[i]
        models = h.getMolFracModelsPtl()
        spaces = ['real-space', 'redshift-space']

        key_array = np.empty((len(models), len(spaces)), dtype=object)

        for k in list(h.slices.keys()):
            if k[-2:] == 'rs':
                col_idx = 1
            else:
                col_idx = 0
            
            row_idx = -1
            for m in range(len(models)):
                if models[m] in k:
                    row_idx = m
            if 'mass' in k:
                key_array[row_idx][col_idx] = k
        
        plib.plot_slices(h, key_array, models, spaces, 
                'HI mass', panel_length, panel_bt, border)
        
        plt.savefig("hiptl_slice_models_vs_space_%03d"%h.snapshot)
        plt.clf()
    
    for i in range(len(h2ptls)):
        h = h2ptls[i]
        models = h.getMolFracModelsPtl()
        spaces = ['real-space', 'redshift-space']

        key_array = np.empty((len(models), len(spaces)), dtype=object)

        for k in list(h.slices.keys()):
            if k[-2:] == 'rs':
                col_idx = 1
            else:
                col_idx = 0
            
            row_idx = -1
            for m in range(len(models)):
                if models[m] in k:
                    row_idx = m    
            key_array[row_idx][col_idx] = k
        
        plib.plot_slices(h, key_array, models, spaces, 
                'HI mass', panel_length, panel_bt, border)
                
        
        plt.savefig("h2ptl_slice_models_vs_space_%03d"%h.header['Redshift'])
        plt.clf()
    

    for i in range(len(vns)):
        v = vns[i]
        models = ['VN18-Particle']
        spaces = ['real-space', 'redshift-space']

        key_array = np.empty((len(models), len(spaces)), dtype=object)

        key_array[0, 0] = 'vn_CICW_mass'
        key_array[0, 1] = 'vn_CICW_massrs'
        #print(list(v.slices.keys()))
        plib.plot_slices(v, key_array, models, spaces, 
                'HI mass', panel_length, panel_bt, border)
        
        plt.savefig("vn_slice_models_vs_space_%03d"%v.header["Redshift"])
        plt.clf()
    
    return

def compare_HI_slices(hiptls, vns, hisubs, panel_length = 3,
            panel_bt = 0.1, border = 0.5):
    
    snaps, redshifts = plib.getSnaps(hiptls+vns+hisubs)
    
    def get_snap_idx(flist, snap):
        for f in range(len(flist)):
            if flist[f].snap == snap:
                return f
        return -1
    
    # make real-space comparison, redshift-space is not needed
    idx_array = np.empty((len(snaps), 3), dtype=object)
    key_array = np.empty_like(idx_array)
    for s in range(len(snaps)):
        hiptl_idx = get_snap_idx(hiptls, snaps[s])
        vn_idx = get_snap_idx(vns, snaps[s])
        hisub_idx = get_snap_idx(hisubs, snaps[s])

        field_indices = [hiptl_idx, vn_idx, hisub_idx]
        modelptl = hiptls[0].getMolFracModelsPtl()[0]
        modelsub = hisubs[0].getMolFracModelsGal()[0]
        keys = [modelptl, 'vn', modelsub]
        for n in range(len(field_indices)):
            idx_array[s, n] = (n, field_indices[n])
            key_array[s, n] = keys[n]
    row_labels = ["z=%03d"%z for z in redshifts]
    plib.compare_slices([hiptls, vns, hisubs], idx_array, key_array,
            row_labels, ["D18-Particle", "VN18-Particle", "D18-Subhalo"],
            "HI mass", panel_length, panel_bt, border)
    
    plt.savefig("HI_comparison_slices_redshift_vs_field.png")
    plt.clf()
    return
            
def compare_neutral_hydrogen_slices(hiptls, h2ptls, panel_length=3, 
        panel_bt = 0.1, border=0.5):

        def get_snap_idx(flist, snap):
            for f in range(len(flist)):
                if flist[f].snap == snap:
                    return f
            return -1
        

        snaps,_ = plib.getSnaps(hiptls+h2ptls)

        for s in range(len(snaps)):
            idx_array = np.empty((len(snaps), 2), dtype=object)
            key_array = np.empty_like(idx_array, dtype=str)
            
            
            
            


def HI_auto_pk(hiptls, hisubs, vns, in_rss = False, panel_length = 3, 
            panel_bt = 0.1, text_space=0.9, border = 0.5, fsize=16):
    """
    Makes HI-auto power spectra plots, for real space or redshift space.
    Each panel represents another redshift.

    hiptls: list of hiptl objects
    hisubs: list of hisubhalo objects
    vns: list of vn objects
    """

    # get the desired keys for each field - if the fields are not
    # in the results, then make the keys an empty list
    if not in_rss:
        if vns:
            vnkeys = ['vn']
        else:
            vnkeys = []
        if hiptls:
            hiptlkeys = plib.rmKeys(['rs'], list(hiptls[0].pks.keys()))
        else:
            hiptlkeys = []
        if hisubs:
            hisubkeys = plib.rmKeys(['rs'], list(hisubs[0].pks.keys()))
        else:
            hisubkeys = []
    else:
        if vns:
            vnkeys = ['vnrs']
        else:
            vnkeys = []
        if hiptls:
            hiptlkeys = plib.fetchKeys(['rs'], list(hiptls[0].pks.keys()))
        else:
            hiptlkeys = []
        if hisubs:
            hisubkeys = plib.fetchKeys(['rs'], list(hisubs[0].pks.keys()))
        else:
            hisubkeys = []
    
    fields = []
    fields.extend(hiptls)
    fields.extend(hisubs)
    fields.extend(vns)

    key_dict = {'hiptl':hiptlkeys, 'hisubhalo':hisubkeys, 'vn':vnkeys}
    yrange = plib.getYrange(fields, key_dict)
    snapshots, _ = plib.getSnaps(fields)

    fig, panels = plib.createFig(panel_length, 1, len(snapshots), panel_bt,
            border, border)
    
    print(fig.get_size_inches())
    # now making each panel
    for i in range(len(panels)):
        plt.sca(panels[i])
        panel_snap = snapshots[i]

        # plot the VN18 that matches the panel's redshift
        for pf in vns:
            if pf.snapshot == panel_snap:
                box = pf.header['BoxSize']
                plib.plotpks(pf.pks['k'], pf.pks, box, pf.resolution,
                        keylist = vnkeys, colors = ['green'],
                        labels = ['V-N18'])
        
        # plot the D18-Subhalo that matches the panel's redshift
        for pf in hisubs:
            if pf.snapshot == panel_snap:
                box = pf.header['BoxSize']
                plib.fillpks(pf.pks['k'], pf.pks, box, pf.resolution,
                        keylist = hisubkeys, color = 'orange',
                        label = 'D18-Subhalo')
        
        # plot the D18-Particle that matches the panel's redshift
        for pf in hiptls:
            if pf.snapshot == panel_snap:
                box = pf.header['BoxSize']
                plib.fillpks(pf.pks['k'], pf.pks, box, pf.resolution,
                        keylist = hiptlkeys, color = 'blue',
                        label = 'D18-Particle')

            
        # cosmetic tasks
        if not i == 0:
            ax = plt.gca()
            ax.set_yticklabels([])
            ax.get_legend().remove()
        else:
            plt.legend(loc = 'upper right')
        plt.ylim(yrange[0], yrange[1])
        plt.xlabel('')
        plt.ylabel('')
        # output textbox onto the plot with redshift
        xts = (hiptls[0].pks['k'][0]) / text_space
        yts = (yrange[0]) / text_space
        
        # needed in every panel
        plt.text(hiptls[0].pks['k'][0]+xts, yrange[0]+yts,
                'z=%.1f'%snapshots[i], fontsize = fsize, ha = 'left', va = 'bottom',
                fontweight = 'bold') 

    figsize = fig.get_size_inches()
    fig.text(border/2/figsize[0], 0.5, r'P(k) (Mpc/h)$^{-3}$',ha = 'center',
            va = 'center', fontsize=fsize)
    fig.text(0.5, border/2/figsize[1], r'k (Mpc/h)$^{-1}$', ha = 'center',
            va = 'center', fontsize=fsize)
    return
if __name__ == '__main__':
    main()
