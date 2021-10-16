import illustris_python as il
import sys
import os
import numpy as np
import h5py as hp
import pickle as pkl

PREFIX = sys.argv.pop(1)
SIMNAME = sys.argv.pop(1)
SNAPSHOT = int(sys.argv.pop(1))
AXIS = int(sys.argv.pop(1))
RESOLUTION = int(sys.argv.pop(1))

sys.argv.pop(0) # removing unneeded script name

RUNNAMES = sys.argv

VERBOSE = int(input("how verbose should the logs be? (0 for limited, 1 for detailed)"))
implemented_fields = ['hiptl', 'hisubhalo', 'galaxy', 'galaxy_dust', 'vn', 'ptl', 'hiptl_nH']
HI_fields = ['hiptl', 'hisubhalo', 'vn', 'hiptl_nH']
matter_fields = ['galaxy','galaxy_dust', 'ptl']

print("output directory prefix:%s"%PREFIX)
print("verbosity:%d"%VERBOSE)
print("simulation name: %s"%SIMNAME)
print("snapshot: %03d"%SNAPSHOT)
print("axis: %d"%AXIS)
print("resolution of grid: %d"%RESOLUTION)
print("runs given: "+str(RUNNAMES))
print("currently implemented fields: "+ str(implemented_fields))

tng_sims = ['L205n2500TNG', 'L352160TNG', 'L751820TNG', 'L75n455TNG', 'L75n455TNG_DM', 'L75n910TNG']
gd = {}
TNG = '/net/nyx/nyx1/diemer/illustris/'
yorpfile = open('yorp.bash','w')

# make the create_grids
