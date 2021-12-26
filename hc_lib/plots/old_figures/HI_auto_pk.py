from hc_lib.plots import plot_lib as plib
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import sys

mpl.rcParams['text.usetex'] = True

def main():
    print("___________MAKING HI AUTO POWER_____________")
    print("loading paths...")
    OUTDIR = sys.argv.pop(1)
    paths = plib.getPaths(OUTDIR)

    print("loading pickle files...")
    hiptls = plib.checkPkls(paths, {'fieldname':'hiptl'})
    vns = plib.checkPkls(paths, {'fieldname':'vn'})
    hisubs = plib.checkPkls(paths, {'fieldname':'hisubhalo'})

    print("plotting individual models for hiptl...")
    hiptl_auto_redshiftR_spaceC_model(hiptls)

    print("plotting individual models for hisubhalo...")
    hisubhalo_auto_redshiftR_spaceC_model(hisubs)

    print("plotting auto power spectra for HI...")    
    HI_auto_redshiftR_spaceC_field(hiptls, hisubs, vns)

    print('___________FINISHED HI AUTO POWER_____________')
    return
def match_snapshot(snapshot, fields):
    for f in fields:
        if snapshot == f.snapshot:
            return f
    return None

def get_suffix(field):
    tup = (field.simname, field.snapshot, field.axis, field.resolution)
    suf = "%sB_%03dS_%dA_%dR"%tup
    return suf

def hiptl_auto_redshiftR_spaceC_model(hiptls, panel_length = 3, 
            panel_bt = 0.33, border = 1, fsize=16):
    
    snapshots, redshifts = plib.getSnaps(hiptls)
    nrows = len(snapshots)
    col_labels = ["Real Space", "Redshift Space", "Comparison", "Distortions"]
    ncols = len(col_labels)
    fig, panels = plib.createFig(panel_length, nrows, ncols, panel_bt,
            border, border)
    
    # getting keys for each part:
    real_keys = plib.fetchKeys(['CICW'],['rs', 'temp'], list(hiptls[0].pks.keys()))
    redsh_keys = plib.fetchKeys(['CICW', 'rs'], ['temp'], list(hiptls[0].pks.keys()))
    
    yrange = [np.inf, 0]

    keys = {'Real Space':real_keys, 'Redshift Space':redsh_keys}
    for i in range(nrows):
        snap = snapshots[i]

        field = match_snapshot(snap, hiptls)
        
        for j in range(ncols):
            plt.sca(panels[i][j])
            ax = plt.gca()
            # comparison column will look different
            if j == 0 or j == 1:
                labels = [st.split('_')[0] for st in keys[col_labels[j]]]
                plib.plotpks(field.pks['k'], field.pks, field.box, field.resolution,
                        keys[col_labels[j]], labels=labels)
                
                ymin, ymax = ax.get_ylim()
                if ymin > 0:
                    yrange[0] = min(yrange[0], ymin)

                yrange[1] = max(yrange[1], ymax)
                plt.ylabel('')    
                
            
            elif j == 2:
                colors = ['blue', 'red']
                for k in range(len(keys)):
                    plib.fillpks(field.pks['k'], field.pks, field.box, field.resolution,
                            keys[col_labels[k]], label = col_labels[k], color= colors[k])
                plt.legend(loc = 'upper right')

                ymin, ymax = ax.get_ylim()
                if ymin > 0:
                    yrange[0] = min(yrange[0], ymin)

                yrange[1] = max(yrange[1], ymax)

                plt.ylabel('')
                
            elif j == 3:
                distortions = {}
                labels = []
                for pkey in keys[col_labels[0]]:
                    distortions[pkey] = field.pks[pkey+'rs']/field.pks[pkey]
                    labels.append(pkey.split('_')[0])
                plib.plotpks(field.pks['k'], distortions, field.box, field.resolution,
                        keys[col_labels[0]], labels=labels)
                plt.ylabel(r'$\frac{P_z(k)}{P_r(k)}$')
                plt.yscale('linear')

            if i == 0:
                ax.xaxis.set_label_position('top')
                plt.xlabel(col_labels[j])
            else:
                plt.xlabel('')
                ax.get_legend().remove()
            if not i == nrows-1:
                ax.xaxis.set_ticklabels([])
            if j == 0:
                plt.text(0.05, 0.05, 'z=%.1f'%redshifts[i], fontsize = fsize, 
                        ha = 'left', va = 'bottom', transform = ax.transAxes)
            else:
                if not j == ncols - 1:
                    ax.yaxis.set_ticklabels([])
            
    for i in range(nrows):
        for j in range(ncols-1):
            plt.sca(panels[i][j])
            plt.ylim(yrange[0], yrange[1])
            
    figsize = fig.get_size_inches()
    fig.text(0.5, border/3/figsize[1], 'k (h/Mpc)', ha='center', va = 'center', 
            fontsize = fsize)

    fig.text(border/3/figsize[0], 0.5, 'P(k) (h/Mpc)$^3$', ha='center', va = 'center', 
            fontsize = fsize, rotation = 'vertical')
    plt.savefig("HI_auto/hiptl_auto_redshiftR_spaceC_models_%s.png"%get_suffix(hiptls[0]))
    plt.clf()
    return
            
def hisubhalo_auto_redshiftR_spaceC_model(hisubs, panel_length=3, panel_bt = 0.33,
            border = 1, fsize = 16):
    snapshots, redshifts = plib.getSnaps(hisubs)
    nrows = len(snapshots)
    col_labels = ["Real Space", "Redshift Space", "Comparison", "Distortions"]
    ncols = len(col_labels)
    fig, panels = plib.createFig(panel_length, nrows, ncols, panel_bt,
            border, border)
    
    # getting keys for each part:
    real_keys = plib.fetchKeys(['CICW'],['rs', 'papa'], list(hisubs[0].pks.keys()))
    redsh_keys = [k+'rs' for k in real_keys]

    yrange = [np.inf, 0]

    keys = [real_keys, redsh_keys]
    for i in range(nrows):
        snap = snapshots[i]

        field = match_snapshot(snap, hisubs)
        
        for j in range(ncols):
            plt.sca(panels[i][j])
            ax = plt.gca()
            # comparison column will look different
            if j == 0 or j == 1:
                labels = [st.split('_')[2] for st in keys[j]]
                plib.plotpks(field.pks['k'], field.pks, field.box, field.resolution,
                        keys[j], labels=labels)
                
                ymin, ymax = ax.get_ylim()
                if ymin > 0:
                    yrange[0] = min(yrange[0], ymin)

                yrange[1] = max(yrange[1], ymax)
                plt.ylabel('')
            
            elif j == 2:
                colors = ['blue', 'red']
                for k in range(len(keys)):
                    plib.fillpks(field.pks['k'], field.pks, field.box, field.resolution,
                            keys[k], label = col_labels[k], color= colors[k])
                plt.legend(loc = 'upper right')
                plt.ylim(yrange[0], yrange[1])
                plt.ylabel('')

            elif j == 3:
                distortions = {}
                labels = []
                for pkey in keys[0]:
                    distortions[pkey] = field.pks[pkey+'rs']/field.pks[pkey]
                    labels.append(pkey.split('_')[2])
                plib.plotpks(field.pks['k'], distortions, field.box, field.resolution,
                        keys[0], labels=labels)
                plt.ylabel(r'$\frac{P_z(k)}{P_r(k)}$')
                plt.yscale('linear')
            ax = plt.gca()
            plt.xlabel('')
            if i == 0:
                ax.xaxis.set_label_position('top')
                plt.xlabel(col_labels[j])
            if not i == nrows-1:
                ax.xaxis.set_ticklabels([])
            if j == 0:
                plt.text(0.05, 0.05, 'z=%.1f'%redshifts[i], 
                        fontsize = fsize, ha = 'center', va = 'center', transform = ax.transAxes)
            else:
                if not j == ncols - 1:
                    ax.yaxis.set_ticklabels([])
    for i in range(nrows):
        for j in range(ncols-1):
            plt.sca(panels[i][j])
            plt.ylim(yrange[0], yrange[1])
            
    figsize = fig.get_size_inches()
    fig.text(0.5, border/3/figsize[1], 'k (h/Mpc)', ha='center', va = 'center', 
            fontsize = fsize)

    fig.text(border/3/figsize[0], 0.5, 'P(k) (h/Mpc)$^3$', ha='center', va = 'center', 
            fontsize = fsize, rotation = 'vertical')
    plt.savefig("HI_auto/hisubhalo_auto_redshiftR_spaceC_models_%s.png"%get_suffix(hisubs[0]))
    plt.clf()
    return

def HI_auto_redshiftR_spaceC_field(hiptls, hisubs, vns, panel_length = 3, 
            panel_bt = 0.33, border = 0.5, fsize=16):
    """
    Makes HI-auto power spectra plots, for real space or redshift space.
    Each panel represents another redshift.

    hiptls: list of hiptl objects
    hisubs: list of hisubhalo objects
    vns: list of vn objects
    """

    # get the desired keys for each field - if the fields are not
    # in the results, then make the keys an empty list


    
    vn_real_keys = plib.fetchKeys(['mass'], ['rs'], list(vns[0].pks.keys()))
    vn_redsh_keys = [k+'rs' for k in vn_real_keys] 
    vn_keys = vn_real_keys + vn_redsh_keys

    hiptl_real_keys = plib.fetchKeys(['mass'], ['rs'], list(hiptls[0].pks.keys()))
    hiptl_redsh_keys = [k+'rs' for k in hiptl_real_keys] 
    hiptl_keys = hiptl_redsh_keys + hiptl_real_keys

    hisub_real_keys = plib.fetchKeys(['diemer'], ['rs', 'papa', '_CIC_'], list(hisubs[0].pks.keys()))
    hisub_redsh_keys = [k+'rs' for k in hisub_real_keys]
    hisub_keys = hisub_redsh_keys + hisub_real_keys

    print(vn_keys)
    print(hiptl_keys)
    print(hisub_keys)

    fields = []
    fields.extend(hiptls)
    fields.extend(hisubs)
    fields.extend(vns)

    key_dict = {'hiptl':hiptl_keys, 'hisubhalo':hisub_keys, 'vn':vn_keys}
    yrange = plib.getYrange(fields, key_dict, False)
    snapshots, redshifts = plib.getSnaps(fields)

    col_labels = ['Real Space', 'Redshift Space', 'Distortions']
    nrows = len(snapshots)
    ncols = len(col_labels)
    xborder = [1.5 * border, border]
    fig, panels = plib.createFig(panel_length, nrows, ncols, panel_bt,
            xborder, border)
    
    # now making each panel
    
    for i in range(nrows):
        snap = snapshots[i]
        vn = match_snapshot(snap, vns)
        hiptl = match_snapshot(snap, hiptls)
        hisub = match_snapshot(snap, hisubs)
        for j in range(ncols):
            plt.sca(panels[i][j])
            if col_labels[j] == 'Real Space':
                plib.plotpks(vn.pks['k'], vn.pks, vn.box, vn.resolution,
                        keylist = vn_real_keys, colors = ['green'],
                        labels = ['VN18-Particle'])

 
                plib.fillpks(hisub.pks['k'], hisub.pks, hisub.box, hisub.resolution,
                        keylist = hisub_real_keys, color = 'orange',
                        label = 'D18-Subhalo')
                
                plib.fillpks(hiptl.pks['k'], hiptl.pks, hiptl.box, hiptl.resolution,
                        keylist = hiptl_real_keys, color = 'blue',
                        label = 'D18-Particle')
                
                plt.ylabel('')
            elif col_labels[j] == 'Redshift Space':
                plib.plotpks(vn.pks['k'], vn.pks, vn.box, vn.resolution,
                        keylist = vn_redsh_keys, colors = ['green'],
                        labels = ['VN18-Particle'])

 
                plib.fillpks(hisub.pks['k'], hisub.pks, hisub.box, hisub.resolution,
                        keylist = hisub_redsh_keys, color = 'orange',
                        label = 'D18-Subhalo')
                
                plib.fillpks(hiptl.pks['k'], hiptl.pks, hiptl.box, hiptl.resolution,
                        keylist = hiptl_redsh_keys, color = 'blue',
                        label = 'D18-Particle')
                plt.ylabel('')
            elif col_labels[j] == 'Distortions':
                
                fields = [hiptl, vn, hisub]
                keys = [hiptl_real_keys, vn_real_keys, hisub_real_keys]
                labels = ['D18-Particle', 'VN18-Particle', 'D18-Subhalo']
                for f in range(len(fields)):
                    distortions = {}
                    for pkey in keys[f]:
                        distortions[pkey] = fields[f].pks[pkey+'rs']/fields[f].pks[pkey]
                    if fields[f].fieldname == 'vn':
                        fld = fields[f]
                        plib.plotpks(fld.pks['k'], distortions, fld.box, fld.resolution,
                                colors=['green'], labels=[labels[f]])
                    else:
                        fld = fields[f]
                        if fld.fieldname == 'hiptl':
                            col = 'blue'
                        else:
                            col = 'orange'
                        plib.fillpks(fld.pks['k'], distortions, fld.box, fld.resolution,
                                color=col)
                    
                    plt.yscale('linear')
                    plt.ylabel(r'$\frac{P_z(k)}{P_r(k)}$')


            ax = plt.gca()
           
            if i == 0 and j == 0:
                plt.legend(loc='upper right')
            else:
                ax.get_legend().remove()

            if i == 0:
                ax.xaxis.set_label_position('top')
                plt.xlabel(col_labels[j])
            else:
                plt.xlabel('')
            
            if not i == nrows - 1:
                ax.set_xticklabels([])
            
            if j == 0:
                plt.text(0.05, 0.05,
                    'z=%.1f'%redshifts[i], fontsize = fsize, ha = 'left', va = 'bottom',
                    fontweight = 'bold', transform = ax.transAxes)
            else:
                ax.set_yticklabels([])
        

    figsize = fig.get_size_inches()
    fig.text(border/3/figsize[0], 0.5, r'P(k) (Mpc/h)$^{-3}$',ha = 'center',
            va = 'center', fontsize=fsize, rotation='vertical')
    fig.text(0.5, border/3/figsize[1], r'k (Mpc/h)$^{-1}$', ha = 'center',
            va = 'center', fontsize=fsize)
    
    plt.savefig("HI_auto/HI_auto_redshiftR_vs_spaceC_field_%s.png"%get_suffix(vns[0]))
    plt.clf()
    return

if __name__ == '__main__':
    main()