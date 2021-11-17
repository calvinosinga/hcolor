from hc_lib.plots import plot_lib as plib
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.gridspec as gspec
import pickle as pkl
import numpy as np
import sys

mpl.rcParams['text.usetex'] = True

def main():
    # remove the script name
    print('________MAKING SLICE PLOTS_________')
    sys.argv.pop(0)
    print("loading paths to pickle files...")
    OUTDIR = sys.argv[0]
    paths = plib.getPaths(OUTDIR)

    print("loading pickle files...")
    h2ptls = plib.checkPkls(paths, {'fieldname':'h2ptl'})
    hiptls = plib.checkPkls(paths, {'fieldname':'hiptl'})
    vns = plib.checkPkls(paths, {'fieldname':'vn'})
    ptls = plib.checkPkls(paths, {'fieldname':'ptl'})
    hisubs = plib.checkPkls(paths, {'fieldname':'hisubhalo'})

    print("now plotting the slices for particle catalog fields...")
    make_ptl_slices(hiptls, h2ptls, vns, ptls)
    
    print("now plotting slices to compare particle catalog fields...")
    compare_ptl_slices(hiptls, h2ptls, vns, ptls)

    print("now comparing HI slices...")
    compare_HI_slices(hiptls, vns, hisubs)

    print('___________FINISHING SLICE PLOTS________')
    return

def get_suffix(field):
    tup = (field.simname, field.snapshot, field.axis, field.resolution)
    suf = "%sB_%03dS_%dA_%dR"%tup
    return suf

def make_ptl_slices(hiptls, h2ptls, vns, ptls, panel_length = 3,
            panel_bt = 0.1, border = 0.5):
    for i in range(len(hiptls)):
        h = hiptls[i]
        models = h.getMolFracModelsPtl()
        spaces = ['Real Space', 'Redshift Space']

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
        
        plt.savefig("slices/hiptl_slice_models_vs_space_%s"%get_suffix(h))
        plt.clf()
    
    for i in range(len(h2ptls)):
        h = h2ptls[i]
        models = h.getMolFracModelsPtl()
        spaces = ['Real Space', 'Redshift Space']

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
                r'H$_2$ mass', panel_length, panel_bt, border)
                
        
        plt.savefig("slices/h2ptl_slice_models_vs_space_%s"%get_suffix(h))
        plt.clf()
    

    for i in range(len(vns)):
        v = vns[i]
        models = ['VN18-Particle']
        spaces = ['Real Space', 'Redshift Space']

        key_array = np.empty((len(models), len(spaces)), dtype=object)

        key_array[0, 0] = 'vn_CICW_mass'
        key_array[0, 1] = 'vn_CICW_massrs'
        #print(list(v.slices.keys()))
        plib.plot_slices(v, key_array, models, spaces, 
                'HI mass', panel_length, panel_bt, border)
        plt.ylabel('')
        plt.savefig("slices/vn_slice_models_vs_space_%s"%get_suffix(v))
        plt.clf()
    
    for i in range(len(ptls)):
        p = ptls[i]
        ptl_types = ['ptl', 'stmass', 'dm']
        ptl_types = [i+'_CICW' for i in ptl_types]
        spaces = ['Real Space', 'Redshift Space']

        key_array = np.empty((len(ptl_types), len(spaces)), dtype=object)


        for i in range(len(ptl_types)):
            for j in range(len(spaces)):
                if j == 1:
                    spc = 'rs'
                else:
                    spc = ''
                key_array[i,j] = ptl_types[i]+spc
        
        plib.plot_slices(p, key_array, ['all', 'stellar', 'dark matter'], spaces, 
                'mass', panel_length, panel_bt*3, border, same_cmap=False)
        
        plt.savefig("slices/ptl_slice_ptltype_vs_space_%s"%get_suffix(p))
        plt.clf()
    return

def compare_ptl_slices(hiptls, h2ptls, vns, ptls, panel_length=3, 
        panel_bt = 0.1, border=0.5):

        def get_snap_idx(flist, snap):
            for f in range(len(flist)):
                if flist[f].snapshot == snap:
                    return f
            return -1
        
        
        snaps, redshifts = plib.getSnaps(hiptls+h2ptls+vns+ptls)
        fields = [hiptls, h2ptls, vns, ptls]
        row_labels = ["z=%0.02f"%z for z in redshifts]
        for s in range(len(snaps)):
            idx_array = np.empty((len(snaps), 4), dtype=object)
            key_array = np.empty_like(idx_array)
            hiidx = get_snap_idx(hiptls, s)
            h2idx = get_snap_idx(h2ptls, s)
            vnidx = get_snap_idx(vns, s)
            ptlidx = get_snap_idx(ptls, s)
            indices = np.array([hiidx, h2idx, vnidx, ptlidx])
            keys = ['GD14_CICW_mass', 'GD14_CICW', 
                    'vn_CICW_mass','ptl_CICW']

            for i in range(len(indices)):
                idx_array[s, i] = (i, indices[i])
                key_array[s, i] = keys[i]
        
        col_labels = ['D18-Particle HI (GD14)', 'D18-Particle H$_2$ (GD14)', 'VN18-Particle',
                'Particle']
        cmap_cycle = ['winter', 'bone', 'plasma', 'jet']
        plib.compare_slices(fields, idx_array, key_array, row_labels, col_labels,
                "mass", panel_length, panel_bt, border, False, cmap_cycle)
        plt.savefig("slices/ptl_slices_comparison_redshift_vs_field_%s.png"%get_suffix(hiptls[0]))
        plt.clf()
        return


def compare_HI_slices(hiptls, vns, hisubs, panel_length = 3,
            panel_bt = 0.1, border = 0.5):
    
    snaps, redshifts = plib.getSnaps(hiptls+vns+hisubs)
    
    def get_snap_idx(flist, snap):
        for f in range(len(flist)):
            if flist[f].snapshot == snap:
                return f
        return -1
    
    # make real-space comparison, Redshift Space is not needed
    idx_array = np.empty((len(snaps), 3), dtype=object)
    key_array = np.empty_like(idx_array)
    for s in range(len(snaps)):
        hiptl_idx = get_snap_idx(hiptls, snaps[s])
        vn_idx = get_snap_idx(vns, snaps[s])
        hisub_idx = get_snap_idx(hisubs, snaps[s])

        field_indices = [hiptl_idx, vn_idx, hisub_idx]

        keys = ['GD14_CICW_mass','vn_CICW_mass', 'm_hi_GD14_map_CICW_diemer']
        for n in range(len(field_indices)):
            idx_array[s, n] = (n, field_indices[n])
            key_array[s, n] = keys[n]
    row_labels = ["z=%0.02f"%z for z in redshifts]
    plib.compare_slices([hiptls, vns, hisubs], idx_array, key_array,
            row_labels, ["D18-Particle", "VN18-Particle", "D18-Subhalo"],
            "HI mass", panel_length, panel_bt, border)
    
    plt.savefig("slices/HI_slices_comparison_redshift_vs_field_%s.png"%get_suffix(hiptls[0]))
    plt.clf()
    return
            

            
            
if __name__ == "__main__":
    main()         
            
