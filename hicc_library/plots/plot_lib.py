import pickle as pkl
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.gridspec as gspec
import copy

mpl.rcParams['text.usetex'] = True
home = 'C:/Users/calvi/AppData/Local/Packages/CanonicalGroupLimited' + \
        '.UbuntuonWindows_79rhkp1fndgsc/LocalState/rootfs/home/cosinga/'
path = home + 'pks/pks/to_laptop/'

def fetchKeys(substrings, keylist):
    res = []
    for sub in substrings:
        for k in keylist:
            if sub in k and not k in res:
                res.append(k)
    
    if 'k' in res:
        res.remove('k')
    if 'Nmodes' in res:
        res.remove('Nmodes')
    if 'r' in res:
        res.remove('r')
    return res

def rmKeys(keywords, keylist):
    klist = copy.copy(keylist)
    for word in keywords:
        for k in klist:
            if word in k:
                klist.remove(k)
    if 'k' in klist:
        klist.remove('k')
    if 'Nmodes' in klist:
        klist.remove("Nmodes")
    if 'r' in klist:
        klist.remove('r')
    return klist

def getYrange(fields, keys_dict, is_X):
    yrange = [np.inf, 0]
    for f in fields:
        if not is_X:
            pks = f.pks
        else:
            pks = f.xpks
        keys = keys_dict[f.fieldname]
        nyq = f.resolution * np.pi / f.box
        nyq_idx = np.argmin(np.abs(pks['k'] - nyq))
        for k in keys:
            pkmax = np.max(pks[k][:nyq_idx])
            pkmin = np.min(pks[k][:nyq_idx])
            if pkmax > yrange[1]:
                yrange[1] = pkmax
            if pkmin < yrange[0] and pkmin > 0:
                yrange[0] = pkmin
    return yrange

def getSnaps(fields):
    snapshots = []
    for f in fields:
        if not f.snapshot in snapshots:
            snapshots.append(f.snapshot)
    snapshots.sort()
    return snapshots

def createFig(panel_length, nrows, ncols, panel_bt, xborder, yborder):
    # border input can be either a list or single number
    if isinstance(xborder, float) or isinstance(xborder, int):
        xborder = [xborder, xborder]
    if isinstance(yborder, float) or isinstance(yborder, int):
        xborder = [yborder, yborder]
    # creating Figure object

    figwidth = panel_length * ncols + panel_bt * (ncols - 1) + \
            xborder[0] + xborder[1]
    figheight = panel_length * nrows + panel_bt * (nrows - 1) + \
            yborder[0] + yborder[1]
    
    fig = plt.figure(figsize=(figwidth, figheight))

    # creating gridspec
    gs = gspec.GridSpec(nrows, ncols)
    plt.subplots_adjust(left= xborder[0]/figwidth, right=1-xborder[1]/figwidth,
            top=1-yborder[1]/figheight, bottom=yborder[0]/figheight,
            wspace=panel_bt, hspace=panel_bt)
    
    # making panels list
    panels = []
    for i in range(nrows):
        col_panels = []
        for j in range(ncols):
            col_panels.append(fig.add_subplot(gs[i,j]))
        panels.append(col_panels)
    
    return fig, panels
        
def plotpks(k, pks, boxsize, resolution, keylist = None, colors = None,
        labels = None, linestyles = None, linewidths = None, nyq = False,
        is_corr = False):
    # get default values
    if keylist is None:
        keylist = list(pks.keys())
    if colors == None:
        colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    if labels == None:
        labels = [i for i in keylist]
    if linestyles==None:
        linestyles = ['solid' for i in keylist]
    if linewidths == None:
        linewidths = [1 for i in keylist]
    
    # unpack the dictionary
    pltpk = np.zeros((len(keylist),len(k)))
    for i in range(len(keylist)):
        pltpk[i, :] = pks[keylist[i]][:]
    
    # if the nyquist fq is desired, plot it here
    nyqval= resolution*np.pi/boxsize
    if is_corr:
        nyqval = 2 * np.pi / nyqval
    if nyq:
        maxy = np.max(pltpk)

        plt.plot((nyqval,nyqval),(0,maxy),'k:')
    
    # Now plotting the pks
    for p in range(pltpk.shape[0]):
        plt.plot(k, pltpk[p,:], color=colors[p], label=r''+labels[p], ls=linestyles[p], lw=linewidths[p])
    plt.xscale('log')
    plt.yscale('log')

    plt.ylabel(r'P(k) (Mpc/h)$^{-3}$')
    plt.xlabel(r'k (Mpc/h)$^{-1}$')
    plt.legend()
    if not nyq:
        plt.xlim(np.min(k), nyqval)
    ax = plt.gca()
    ax.tick_params(which='both',direction='in')
    return
    
def plot2Dpk(kpar, kper, pk, do_axes_labels = True):
    cmap = copy.copy(mpl.cm.get_cmap("plasma"))
    cmap.set_under('w')
    kpar = np.unique(kpar)
    kper = np.unique(kper)
    paridx = np.where(kpar>5)[0][0]
    peridx = np.where(kper>5)[0][0]
    KPAR, KPER = np.meshgrid(kpar[:paridx], kper[:peridx])
    pk = np.log10(np.reshape(pk,(len(kper),len(kpar))))
    levs = [-2,-1.5,-1,-0.5,0,0.5,1,1.5,2,2.5,3,3.5,4]
    plt.contour(KPAR, KPER, pk[:paridx,:peridx], vmin=-2, vmax=4, levels=levs, colors='k', linestyles='solid')
    res = plt.imshow(pk[:paridx,:peridx], vmin=-2, vmax=4, extent=(0,kpar[paridx-1],0,kper[peridx-1]), origin='lower', cmap=cmap)
    plt.xlabel(r"kpar (h/Mpc)")
    plt.ylabel(r"kper (h/Mpc)")
    plt.colorbar()
    return

def plotxis(r, xis, boxsize, resolution, keylist = None, colors = None,
        labels = None, linestyles = None, linewidths = None, nyq = False):
    plotpks(r, xis, boxsize, resolution, keylist, colors, labels,
            linestyles, linewidths, nyq, is_corr = True)
    plt.ylabel(r'$\xi$(r) (Mpc/h)$^{3}$')
    plt.xlabel(r'r (Mpc/h)')
    return

def fillpks(k, pks, boxsize, resolution, keylist = None, label = '', 
        color = 'blue', dark_edges = False, linestyle = '-', nyq = False):
    
    # get default values
    if keylist == None:
        keylist = list(pks.keys())
    
    # unpack dictionary
    pltpk = np.zeros((len(keylist), len(k)))
    for i in range(len(keylist)):         
        pltpk[i,:] = pks[keylist[i]][:]
    
    # make nyquist plot if desired
    fq= resolution*np.pi/boxsize
    
    if nyq:
        maxy = np.max(pltpk)
        plt.plot((fq,fq),(0,maxy),'k:')
    
    # make plot
    mxpk = np.max(pltpk, axis=0)
    mnpk = np.min(pltpk, axis=0)
    plt.fill_between(k, mnpk, mxpk, label=label, color=color, alpha=0.55)
    if dark_edges:
        plt.plot(k, mnpk, color=color, linestyle=linestyle)
        plt.plot(k, mxpk, color=color, linestyle=linestyle)
    plt.legend()
    plt.xscale('log')
    plt.yscale('log')
    
    plt.ylabel(r'P(k) (Mpc/h)$^{-3}$')
    plt.xlabel(r'k (Mpc/h)$^{-1}$')
    ax = plt.gca()
    ax.tick_params(which='both',direction='in')
    if not nyq:
        plt.xlim(np.min(k), fq)
    return
