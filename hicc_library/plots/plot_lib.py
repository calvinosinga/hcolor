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

def getAuto(fn, box, snapshot, axis, resolution):
    s = path+'%sgrid_%sB_%03dS_%dA_%dR'%(fn,box,snapshot,axis,resolution)
    if os.path.exists(s+'.hdf5.pkl'):
        return pkl.load(open(s+'.hdf5.pkl', 'rb'))
    else:
        return pkl.load(open(s+'.%d.hdf5.pkl', 'rb'))
        
def plotpks(k, pks, boxsize, resolution, keylist = None, colors = None,
        labels = None, linestyles = None, linewidths = None, nyq = False):
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
    fq= resolution*np.pi/boxsize
    if nyq:
        maxy = np.max(pltpk)

        plt.plot((fq,fq),(0,maxy),'k:')
    
    # Now plotting the pks
    for p in range(pltpk.shape[0]):
        plt.plot(k, pltpk[p,:], color=colors[p], label=r''+labels[p], ls=linestyles[p], lw=linewidths[p])
    plt.xscale('log')
    plt.yscale('log')
    plt.ylabel(r'P(k) (Mpc/h)$^{-3}$')
    plt.xlabel(r'k (Mpc/h)$^{-1}$')
    plt.legend()
    if not nyq:
        plt.xlim(np.min(k), fq)
    ax = plt.gca()
    ax.tick_params(which='both',direction='in')
    return
    
def plot2Dpk(kpar, kper, pk):
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
            linestyles, linewidths, nyq)
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