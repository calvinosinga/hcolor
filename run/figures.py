import pickle as pkl
from hc_lib.plots.results import ResultLibrary
import hc_lib.plots.figures.HI_auto as HIfig
import sys

OUTPATH = sys.argv[1]

def main():
    rlib = ResultLibrary()
    rlib.addResults(directory=OUTPATH)

    hiptl_auto(rlib)    
    return

# Do this part later
# def histograms(rl):
#     hists = rl
#     for run in hists:
#         for gal_res in run:
#             plt.

def hiptl_auto(rl):
    ip = {}
    ip['fieldname'] = 'hiptl'
    ip['simname'] = 'tng100'
    ip['axis'] = 0
    ip['grid_resolution'] = 800
    ip['is_auto'] = True
    ip['map'] = 'mass'
    HIfig.redshiftR_spaceC_model(rl, ip)
     
    
     
    return


main()

