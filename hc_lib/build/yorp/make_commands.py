import illustris_python as il
import numpy as np
import h5py as hp
import pickle as pkl
from hc_lib.build.input import Input
from hc_lib.build.gd import IODict


tng_sims = ['L205n2500TNG', 'L352160TNG', 'L751820TNG', 'L75n455TNG', 'L75n455TNG_DM', 'L75n910TNG']
TNG = '/net/nyx/nyx1/diemer/illustris/'
HCOLOR = '/home/cosinga/hcolor/'
OUT = '/yorp16a/cosinga/'

ioobj = Input()
rp = ioobj.getParams()
runs = ioobj.getRuns()

gdobj = IODict(rp, runs, OUT, TNG, HCOLOR)
gdobj.add('TREECOOL', HCOLOR + 'TREECOOL_fg_dec11')



    
