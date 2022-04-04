from hc_lib.plots.container import PostResult
import site
import pickle as pkl
import numpy as np
import copy
import seaborn as sb

def getCdict():
    cdict = {}
    cdict['real'] = 'green'
    cdict['redshift'] = 'orange'
    cdict['red'] = 'red'
    cdict['blue'] = 'blue'
    cdict['resolved'] = 'grey'
    cdict['ratio'] = 'purple'
    zevo = {}
    zevo['rsd'] = 'YlGn'
    for k, v in cdict.items():
        zevo[k] = sb.color_palette(v.capitalize() + 's', 5)
    cdict['zevo'] = zevo
    cdict['rsd'] = 'yellowgreen'
    return cdict

def siteFG():
    FGPATH = '/homes/cosinga/figrid/'
    site.addsitedir(FGPATH)
    return

def load(box, snap, axis, res, filename, dirname = 'fiducial'):
    base = '/lustre/cosinga/hcolor/output/'
    path = '%s%s_%sB_%03dS_%dA_%dR/results/'%(base, dirname, box, 
            snap, axis, res)

    filepath = '%s%s_%sB_%03dS_%dA_%dR.pkl_rlib.pkl'%(path,
            filename, box, snap, axis, res)
    f = pkl.load(open(filepath, 'rb'))
    return f


def logAxes(fg):
    axkw = {}
    axkw['xscale'] = 'log'
    axkw['yscale'] = 'log'
    fg.setAxisParams(axkw)
    return

def setFacecolor(fg, fcolors):
    for i in range(fcolors.shape[0]):
        for j in range(fcolors.shape[1]):
            idx = (i, j)
            fc = fcolors[idx]
            fg.axes[idx].set_facecolor(fc)
    return

def setNyq(fg, xmin, res, box, shift = 0):
    nyq = res * np.pi / box
    fg.setAxisParams({'xlim':[xmin, nyq - shift]})
    fg.matchDefaultLimits()
    return

def pklabels(fg, xpos = [], ypos = [], ysub = '', xtxtkw = {}, ytxtkw = {}):
    xtext = 'k (cMpc/h)$^{-1}$'
    ytext = 'P$_{' + ysub + '}$ (k) (cMpc/h)$^{-3}$'
    if not xpos:
        xpos = [(fg.xborder[0] + 0.5 *  np.sum(fg.panel_widths)) / fg.figsize[0], 0]
    fg.makeXLabel(xtext, xpos, xtxtkw)
    fg.makeYLabel(ytext, ypos, ytxtkw)
    return

def makeRSD(datalist):
    from figrid.data_container import DataContainer
    ip = {'space':'real'}
    real = datalist.getMatching(ip)
    rsdlist = []
    for dc in real:
        mattr = copy.deepcopy(dc.attrs)
        rmattr = []
        for k in mattr:
            if 'runtime' in k or 'space' in k:
                rmattr.append(k)
        for rm in rmattr:
            del mattr[rm]
        mattr['space'] = 'redshift'

#        print(mattr)
        redshift = datalist.getMatching(mattr)
#        print(redshift)
#        print(len(redshift))
        redshift = redshift[0]
        data = [dc.data[0], redshift.data[1]/dc.data[1]]
        rsd = DataContainer(data)
        mattr['space'] = 'rsd' 
        rsd.update(mattr)
        rsdlist.append(rsd)
    return rsdlist

def makeBlueRedRatio(datalist):
    from figrid.data_container import DataContainer
    ip = {'color':'blue'}
    blues = datalist.getMatching(ip)
    ratiolist = []
    for dc in blues:
        mattr = copy.deepcopy(dc.attrs)
        rmattr = []
        for k in mattr:
            if 'runtime' in k or 'color' in k:
                rmattr.append(k)
        for rm in rmattr:
            del mattr[rm]
        mattr['color'] = 'red'

        reds = datalist.getMatching(mattr)
        if len(reds) > 1:
            print('more than one corresponding red for a blue')
        reds = reds[0]
        data = [dc.data[0], reds.data[1]/dc.data[1]]
        ratio = DataContainer(data)
        mattr['color'] = 'ratio' 
        ratio.update(mattr)
        ratiolist.append(ratio)
    return ratiolist

def plotOnes(fg, idx):
    p = fg.axes[idx]
    xlim = p.get_xlim()
    p.plot(xlim, [1, 1], color = 'black', linestyle = ':')
    return
