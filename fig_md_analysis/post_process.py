#!/usr/bin/env python3

import pickle as pkl
import h5py as hp
import numpy as np
import glob
import copy
import site

SPECS = {}
SPECS['all'] = ['box', 'simname', 'grid_resolution', 'snapshot', 'axis', 'path', 'mas', 'space']
SPECS['hisubhalo'] = ['model', 'HI_res', 'censat']
SPECS['galaxy'] = ['color', 'gal_species', 'gal_res', 'color_cut', 'censat']
SPECS['ptl'] = ['ptl_species']
SPECS['hiptl'] = ['model']
SPECS['vn'] = []

def siteFG():
    FGPATH = '/home/cosinga/figrid/'
    site.addsitedir(FGPATH)
    return

def loadpks(dl):
    path = '/home/cosinga/scratch/hcolor/output/*/results/*.pkl_rlib.pkl'
    filenames = glob.glob(path)
    total = 0
    for f in range(len(filenames)):
        fl = pkl.load(open(filenames[f], 'rb'))
        newprops = {'path':filenames[f].split('/')[6].split('_')[0]}
        if 'pk' in fl.results:
            newprops['result_type'] = 'pk'
            total += len(fl.results['pk'])
            dl.loadResults(fl.results['pk'], newprops)
        if '2Dpk' in fl.results:
            newprops['result_type'] = '2Dpk'
            total += len(fl.results['2Dpk'])
            dl.loadResults(fl.results['2Dpk'], newprops)
        if 'xi' in fl.results:
            newprops['result_type'] = 'xi'
            total += len(fl.results['xi'])
            dl.loadResults(fl.results['xi'])
        print("%.2f"%(f/len(filenames)*100) + r"% loaded")
    
    return dl

def makeBias(datalist):
    from figrid.data_container import DataContainer
    biaslist = []
    
    crosses = datalist.getMatching({'is_auto' : False, 'path':['fiducial']})
    for cx in crosses:
        fns = cx.get('fieldname').split('_')
        if 'dust' in fns:
            continue
        autos = []
        for f in fns:
            attrlist = copy.deepcopy(SPECS['all'])
            attrlist.extend(SPECS[f])
            attr = {'is_auto':True, 'fieldname':f}
            for at in attrlist:
                attr[at] = cx.get(at)
            matches = datalist.getMatching(attr)
            if len(matches)>1:
                print('too many matches %d'%len(matches))
                for m in matches:
                    print(m.attrs)
            elif len(matches) == 0:
                print('no matches found')
                print(attr)
                print(cx.attrs)
            else:
                auto = matches[0]
                data = [cx.data[0], cx.data[1] / auto.data[1]]
                dc = DataContainer(data)
                dc.update(copy.deepcopy(cx.attrs))
                dc.add('post_process', 'theory_bias')
                dc.add('numerator', cx.get('fieldname'))
                dc.add('denominator', auto.get('fieldname'))
                biaslist.append(dc)
                autos.append(auto)
        if len(autos) == 2:
            for a in range(len(autos)):
                data = [autos[a].data[0], np.sqrt(autos[a].data[1] / autos[(a+1)%2].data[1])]
                dc = DataContainer(data)
                dc.update(copy.deepcopy(cx.attrs))
                dc.add('post_process', 'obs_bias')
                dc.add('numerator', autos[a].get('fieldname'))
                dc.add('denominator', autos[(a+1)%2].get('fieldname'))
                biaslist.append(dc)

            data = [autos[0].data[0], cx.data[1] / np.sqrt(autos[0].data[1] * autos[1].data[1])]
            dc = DataContainer(data)
            dc.update(copy.deepcopy(cx.attrs))
            dc.add('post_process', 'corr_coef')
            biaslist.append(dc)
            
        del attr
    return biaslist


def makeCoef(datalist, path):
    print("making biases")
    from figrid.data_container import DataContainer
    biaslist = []
    
    crosses = datalist.getMatching({'is_auto' : False, 'path':path})
    cx_count = 0
    pnt_threshold = 0.05
    for cx in crosses:
        fns = cx.get('fieldname').split('_')
        if 'dust' in fns:
            continue
        autos = []
        for f in range(len(fns)):
            attrlist = copy.deepcopy(SPECS['all'])
            attrlist.extend(SPECS[fns[f]])
            attr = {'is_auto':True, 'fieldname':fns[f]}
            for at in attrlist:
                attr[at] = cx.get(at)
            
            if 'censat' in attr:
                if '_' in attr['censat']:
                    attr['censat'] = attr['censat'].split('_')[f]
            matches = datalist.getMatching(attr)
            if len(matches)>1:
                print('too many matches %d'%len(matches))
                for m in matches:
                    print(m.attrs)
            elif len(matches) == 0:
                print('no matches found')
                print(attr)
                print(cx.attrs)
            else:
                auto = matches[0]
#                 data = [cx.data[0], cx.data[1] / auto.data[1]]
#                 dc = DataContainer(data)
#                 dc.update(copy.deepcopy(cx.attrs))
#                 dc.add('post_process', 'theory_bias')
#                 dc.add('numerator', cx.get('fieldname'))
#                 dc.add('denominator', auto.get('fieldname'))
#                 biaslist.append(dc)
                autos.append(auto)
        if len(autos) == 2:
#             for a in range(len(autos)):
#                 data = [autos[a].data[0], np.sqrt(autos[a].data[1] / autos[(a+1)%2].data[1])]
#                 dc = DataContainer(data)
#                 dc.update(copy.deepcopy(cx.attrs))
#                 dc.add('post_process', 'obs_bias')
#                 dc.add('numerator', autos[a].get('fieldname'))
#                 dc.add('denominator', autos[(a+1)%2].get('fieldname'))
#                 biaslist.append(dc)

            data = [autos[0].data[0], cx.data[1] / np.sqrt(autos[0].data[1] * autos[1].data[1])]
            dc = DataContainer(data)
            dc.update(copy.deepcopy(cx.attrs))
            dc.add('post_process', 'corr_coef')
            biaslist.append(dc)
        cx_count += 1
        if cx_count / len(crosses) >= pnt_threshold:
            print("calculated bias for %.2f"%pnt_threshold)
            pnt_threshold += 0.05
        del attr
    return biaslist


siteFG()
from figrid.data_sort import DataSort
ds = DataSort()
ds = loadpks(ds)
blist = makeBias(ds)
ds.extend(blist)
gallist = makeCoef(ds, 'galbt')
hilist = makeCoef(ds, 'HIbt')
ds.extend(gallist); ds.extend(hilist)

pkl.dump(ds, open('/home/cosinga/scratch/hcolor/fig_md_analysis/10-27_datasort.pkl', 'wb'), pkl.HIGHEST_PROTOCOL)


countdict = {}
sumdict = {}
path = '/home/cosinga/scratch/hcolor/output/*/grids/*.hdf5'
filenames = glob.glob(path)
for flnm in filenames:
    countdict[flnm] = {}
    sumdict[flnm] = {}
    f = hp.File(flnm, 'r')
    keys = list(f.keys())
    for k in keys:
        try:
            countdict[flnm][k] = f[k].attrs["count"]
            sumdict[flnm][k] = f[k].attrs["grid_sum"]
        except KeyError:
            print(flnm, k)
grid_data = {}
grid_data['counts'] = countdict
grid_data['sums'] = sumdict

pkl.dump(grid_data, open("10-27_grid_data.pkl", 'wb'), pkl.HIGHEST_PROTOCOL)
