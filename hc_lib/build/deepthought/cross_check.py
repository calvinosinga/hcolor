#!/usr/bin/env python3

import sys
from hc_lib.fields.ptl import ptl
from hc_lib.fields.galaxy import galaxy, galaxy_dust
from hc_lib.fields.hiptl import hiptl, h2ptl
from hc_lib.fields.hisubhalo import hisubhalo, h2subhalo
from hc_lib.fields.vn import vn

############### INPUTS #########################
simname = 'tng100'
snapshot = 99
axis = 0
resolution = 800
verbose = 1
pkl_path = ''
###############################################

tests = [sys.argv[1], sys.argv[2]]
fields = []
print(tests)
def printgp(field):
    gps = field.gridprops
    print('grids in %s'%field.fieldname)
    for gp in gps:
        print(gps[gp].props)
    print()
    fields.append(field)
    return

def getCrosses(gps1, gps2):
    count = 0
    for ii in gps1:
        for jj in gps2:
            i = gps1[ii]
            j = gps2[jj]
            
            if i.isCompatible(j) and j.isCompatible(i):
                print('COMPATIBLE:')
                print(i.props)
                print()
                print(j.props)
                print('\n')
                count += 1
            #print(i.isCompatible(j))
            #print(j.isCompatible(i))
    print('total compatible xpks: %d'%count)
    return



if 'galaxy_dust' in tests:
    galaxy_dust = galaxy_dust(simname, snapshot, axis, resolution, pkl_path, verbose, '', '')
    printgp(galaxy_dust)

elif 'galaxy' in tests:
    gal = galaxy(simname, snapshot, axis, resolution, pkl_path, verbose, '')
    printgp(gal)

if 'hiptl' in tests:
    hiptl = hiptl(simname, snapshot, axis, resolution, 0, pkl_path, verbose, '%d','%d')
    printgp(hiptl)

elif 'h2ptl' in tests:
    h2ptl = h2ptl(simname, snapshot, axis, resolution, 0, pkl_path, verbose, '%d','%d')
    printgp(h2ptl)

if 'ptl' == tests[0] or 'ptl' == tests[1]:
    ptl = ptl(simname, snapshot, axis, resolution, 0, pkl_path, verbose, '%d')
    printgp(ptl)

if 'hisubhalo' in tests:
    hisubhalo = hisubhalo(simname, snapshot, axis, resolution, pkl_path, verbose, '', '')
    printgp(hisubhalo)

elif 'h2subhalo' in tests:
    h2subhalo = h2subhalo(simname, snapshot, axis, resolution, pkl_path, verbose, '', '')
    printgp(h2subhalo)

if 'vn' in tests:
    vn = vn(simname, snapshot, axis, resolution, 0, pkl_path, verbose, '%d', '%d')
    printgp(vn)
if tests[1] == 'galaxy':
    fields.append(galaxy(simname, snapshot, axis, resolution, pkl_path, verbose, ''))
getCrosses(fields[0].gridprops, fields[1].gridprops)


