import matplotlib.pyplot as plt
import matplotlib as mpl
import pickle as pkl
from hc_lib.plots.results import ResultLibrary
import hc_lib.plots.figures.hiptl as fighiptl
import sys

OUTPATH = sys.argv[1]

def main():
    rlib = ResultLibrary()
    rlib.addResults(directory=OUTPATH)

    
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
    
    # 
    return


main()

