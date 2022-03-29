from hc_lib.plots.container import PostResult
import site
import pickle as pkl
import numpy as np

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

def printAttrs(dl, attrs):
    for a in attrs:
        print('data for %s'%a)
        print(dl.getAttrVals(a))

    return

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
    fg.makeXLabel(xtext, xpos, xtxtkw)
    fg.makeYLabel(ytext, ypos, ytxtkw)
    return

