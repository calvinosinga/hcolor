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

def printgp(field):
    gps = field.gridprops
    print('grids in %s'%gps[0].props['fieldname'])
    for gp in gps:
        print(gp.props)
    print()
    fields.append(field)
    return

def getCrosses(gps1, gps2):
    for i in gps1:
        for j in gps2:
            if i.isCompatible(j) and j.isCompatible(i):
                print('COMPATIBLE:')
                print(i.props)
                print()
                print(j.props)
                print('\n')
            else:
                print('NOT COMPATIBLE:')
                print(i.props)
                print()
                print(j.props)
                print('\n')

    return



if 'galaxy_dust' in tests:
    galaxy_dust = galaxy_dust(simname, snapshot, axis, resolution, pkl_path, verbose, '', '')
    printgp(galaxy_dust)

elif 'galaxy' in tests:
    galaxy = galaxy(simname, snapshot, axis, resolution, pkl_path, verbose, '')
    printgp(galaxy)

elif 'hiptl' in tests:
    hiptl = hiptl(simname, snapshot, axis, resolution, 0, pkl_path, verbose, '','')
    printgp(hiptl)

elif 'h2ptl' in tests:
    h2ptl = h2ptl(simname, snapshot, axis, resolution, 0, pkl_path, verbose, '','')
    printgp(h2ptl)

elif 'ptl' in tests:
    ptl = ptl(simname, snapshot, axis, resolution, 0, pkl_path, verbose, '')
    printgp(ptl)

elif 'hisubhalo' in tests:
    hisubhalo = hisubhalo(simname, snapshot, axis, resolution, pkl_path, verbose, '', '')
    printgp(hisubhalo)

elif 'h2subhalo' in tests:
    h2subhalo = h2subhalo(simname, snapshot, axis, resolution, pkl_path, verbose, '', '')
    printgp(h2subhalo)

elif 'vn' in tests:
    vn = vn(simname, snapshot, axis, resolution, pkl_path, verbose, '', '')
    printgp(vn)

getCrosses(fields[0].gridprops, fields[1].gridprops)


