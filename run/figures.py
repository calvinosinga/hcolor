from hc_lib.plots.results import ResultLibrary
import hc_lib.plots.figures.hiptl_auto as hiptlFig
import sys
import os
import copy

sys.argv.pop(0)
SAVEPATH = sys.argv.pop(0)
OUTPATHS = sys.argv

def main():
    if not os.path.isdir(SAVEPATH):
        os.mkdir(SAVEPATH)
    
    rlib = ResultLibrary()
    for OUTPATH in OUTPATHS:
        rlib.addResults(directory=OUTPATH)

    hiptlAuto(rlib)
    return

# Do this part later
# def histograms(rl):
#     hists = rl
#     for run in hists:
#         for gal_res in run:
#             plt.

def hiptlAuto(rl):
    print('_____________ MAKING HIPTL AUTO POWER SPECTRA PLOTS ______________')
    cc = copy.copy # used often, so just made shortcut
    rl.printLib()
    # create directory to save figures in
    saveDirPath = SAVEPATH+'hiptl_auto/'
    if not os.path.isdir(saveDirPath):
        os.mkdir(saveDirPath)
    
    baseIncludeProps = {}
    baseIncludeProps['fieldname'] = 'hiptl'
    baseIncludeProps['simname'] = 'tng100'
    baseIncludeProps['axis'] = 0
    baseIncludeProps['grid_resolution'] = 800
    baseIncludeProps['is_auto'] = True

    ip = cc(baseIncludeProps)
    ip['map'] = 'mass'
    hiptlFig.redshiftR_spaceC_model(rl, baseIncludeProps, saveDirPath)
     
    ip = cc(baseIncludeProps)
    ip['snapshot'] = 99
    hiptlFig.modelR_spaceC_map(rl, ip, saveDirPath)
    
    
    return


main()

