from hc_lib.plots.fig_lib import FigureLibrary
import copy
import illustris_python as il
import h5py as hp
import numpy as np
cc = copy.copy
################## METHODS ###########################
tng99_path = '/lustre/cosinga/L75n1820TNG/'
def HIslices(rl, bip):
    ip = cc(bip)
    ip['fieldname'] = ['vn','hiptl', 'hisubhalo']
    ip['model'] = ['GD14', 'm_hi_GD14_map']
    ip['map'] = ['mass']
    ip['snapshot'] = 99
    del ip['space']
    rowp = 'redshift'
    colp = 'fieldname'
    panelp = 'slice'

    figArr, rowlabels, collabels = rl.organizeFigure(ip, rowp, colp, panelp)
    # get hisubhalo data
    f = il.groupcat.loadSubhalos(tng99_path + 'output/', 99, fields = ['SubhaloPos', 'SubhaloVel'])
    h = hp.File('/lustre/cosinga/L75n1820TNG/postprocessing/hih2/hih2_galaxy_099.hdf5', 'r')
    head = il.groupcat.loadHeader(tng99_path + 'output/', 99)

    ids = h['id_subhalo'][:]
    ids = ids.astype(np.int32)
    pos = f['SubhaloPos'][ids] / 1e3 * head['Time']
    vel = f['SubhaloVel'][ids]
    boxsize = head["BoxSize"]
    hubble = head["HubbleParam"]*100
    redshift = head['Redshift']
    factor = (1+redshift)/hubble
    rspos = pos[:,0] + vel[:,0]*factor
    rspos[:,0] = np.where((rspos[:,0]>boxsize) | (rspos[:,0]<0), 
            (rspos[:,0]+boxsize)%boxsize, rspos[:,0])
    
    # 
    





