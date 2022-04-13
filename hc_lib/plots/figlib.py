import site
import pickle as pkl
import numpy as np
import copy
import glob
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
    cdict['vn'] = 'firebrick'
    cdict['hisubhalo'] = 'sandybrown'
    cdict['hiptl'] = 'saddlebrown'
    return cdict

def getBorders():
    xborder = [0.3, 0.1]
    yborder = [0.1, 0.3]
    return xborder, yborder

def getXlim():
    xlim = [0.11866199299595938, 20]
    return xlim

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

def loadpks(dl):
    
    path = '/lustre/cosinga/hcolor/output/*/results/*.pkl_rlib.pkl'
    filenames = glob.glob(path)
    for f in filenames:
        f = pkl.load(open(f, 'rb'))
        dl.loadResults(f.results['pk'])
    return dl

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
        xpos = [(fg.xborder[0] + 0.5 *  (np.sum(fg.panel_widths) + np.sum(fg.wspace))) / fg.figsize[0], 0]
    if not ypos:
        ypos = [0, (fg.yborder[1] + 0.5 * (np.sum(fg.panel_heights) + np.sum(fg.hspace))) / fg.figsize[1]]
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
            print('%d corresponding reds for a blue:'%len(reds))
            print("BLUE ATTRS:")
            print(blue.attrs)
            print("RED ATTRS:")
            for r in reds:
                print(r.attrs)
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

def makeObsBias(nums, denom):
    from figrid.data_container import DataContainer
    biaslist = []
    for n in nums:
        data = [n.data[0], np.sqrt(n.data[1] / denom.data[1])]
        dc = DataContainer(data)

        dc.update(copy.deepcopy(n.attrs))
        dc.add('figlib_process', 'obs_bias')
        biaslist.append(dc)
    return biaslist
