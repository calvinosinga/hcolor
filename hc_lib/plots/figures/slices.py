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
    ptls = plib.checkPkls(paths, {'fieldname':'ptl'})
    make_ptl_slices(hiptls, h2ptls, vns, ptls)

    hisubs = plib.checkPkls(paths, {'fieldname':'hisubhalo'})

    #compare_HI_slices(hiptls, vns, hisubs)
    return


def make_ptl_slices(hiptls, h2ptls, vns, ptls, panel_length = 3,
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
                
        
        plt.savefig("h2ptl_slice_models_vs_space_%03d"%h.snapshot)
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
        
        plt.savefig("vn_slice_models_vs_space_%03d"%v.snapshot)
        plt.clf()
    
    for i in range(len(ptls)):
        p = ptls[i]
        ptl_types = ['ptl', 'stmass', 'dm']
        ptl_types = [i+'_CICW' for i in ptl_types]
        spaces = ['real-space', 'redshift-space']

        key_array = np.empty((len(ptl_types), len(spaces)), dtype=object)


        for i in range(len(ptl_types)):
            for j in range(len(spaces)):
                if j == 1:
                    spc = 'rs'
                else:
                    spc = ''
                key_array[i,j] = ptl_types[i]+spc
        
        plib.plot_slices(p, key_array, ['all', 'stellar', 'dark matter'], spaces, 
                'mass', panel_length, panel_bt, border)
        
        plt.savefig("ptl_slice_ptltype_vs_space_%03d"%p.snapshot)
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
            
            
if __name__ == "__main__":
    main()         
            