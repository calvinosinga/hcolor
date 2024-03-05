import illustris_python as il
import h5py as hp
import numpy as np
import pickle as pkl
from figrid.data_sort import DataSort
from figrid.data_container import DataContainer
from figrid.figrid import Figrid
from Pk_library import Pk

SIMPATH = '/home/cosinga/scratch/L205n2500TNG/'
head = il.groupcat.loadHeader(SIMPATH + 'output', 50)
h = head['HubbleParam']
box = head['BoxSize']

def get_halo_data(ss):
    data = {}
    f = il.groupcat.loadHalos(SIMPATH + 'output', ss, ['Group_M_Crit200', 'GroupPos', 'GroupFirstSub'])
    data['m200c'] = f['Group_M_Crit200'] * 1e10 / h
    data['x'] = f['GroupPos'] / 1e3
    out_mask = data['x'] >= 75
    data['x'][out_mask] = data['x'][out_mask] - 75
    data['cent_idx'] = f['GroupFirstSub']
    f = hp.File(SIMPATH + 'postprocessing/halo_structure_%03d.hdf5'%ss, 'r')
#     data['form'] = f['a_form'][:]
    data['c200c'] = f['c200c'][:]
    return data

def get_gal_data(ss):
    data = {}
    f = il.groupcat.loadSubhalos(SIMPATH + 'output', ss, ['SubhaloPos', 'SubhaloGrNr', 'SubhaloMassType', 'SubhaloStellarPhotometrics'])
    data['x'] = f['SubhaloPos'] / 1e3
    data['halo_idx'] = f['SubhaloGrNr']
    data['stmass'] = f['SubhaloMassType'][:, 4] * 1e10 / h
    data['gr'] = f['SubhaloStellarPhotometrics'][:, 4] - f['SubhaloStellarPhotometrics'][:, 5]
    return data

def get_hi_data(ss):

    return


def get_blue_mask(gr, ss):
    if ss == 99:
        return (gr <= 0.6)
    elif ss == 67:
        return gr <= 0.55
    elif ss == 50:
        return gr <= 0.5
    else:
        raise ValueError()
    
def get_res_mask(stmass):
    return stmass >= 2e8

def CICW(npoints, pos, boxsize, mass):
    grid = np.zeros((npoints, npoints, npoints), dtype = np.float32)

    ptls = pos.shape[0]; coord = pos.shape[1]; dims = grid.shape[0]
    inv_cell_size = dims/boxsize
    
    index_d = np.zeros(3, dtype=np.int64)
    index_u = np.zeros(3, dtype=np.int64)
    d = np.zeros(3)
    u = np.zeros(3)

    for i in range(ptls):
        for axis in range(coord):
            dist = pos[i,axis] * inv_cell_size
            u[axis] = dist - int(dist)
            d[axis] = 1 - u[axis]
            index_d[axis] = (int(dist))%dims
            index_u[axis] = index_d[axis] + 1
            index_u[axis] = index_u[axis]%dims #seems this is faster
        grid[index_d[0],index_d[1],index_d[2]] += d[0]*d[1]*d[2]*mass[i]
        grid[index_d[0],index_d[1],index_u[2]] += d[0]*d[1]*u[2]*mass[i]
        grid[index_d[0],index_u[1],index_d[2]] += d[0]*u[1]*d[2]*mass[i]
        grid[index_d[0],index_u[1],index_u[2]] += d[0]*u[1]*u[2]*mass[i]
        grid[index_u[0],index_d[1],index_d[2]] += u[0]*d[1]*d[2]*mass[i]
        grid[index_u[0],index_d[1],index_u[2]] += u[0]*d[1]*u[2]*mass[i]
        grid[index_u[0],index_u[1],index_d[2]] += u[0]*u[1]*d[2]*mass[i]
        grid[index_u[0],index_u[1],index_u[2]] += u[0]*u[1]*u[2]*mass[i]

    return grid


