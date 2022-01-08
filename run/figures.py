from hc_lib.plots.results import ResultLibrary
import hc_lib.plots.figures.hiptl_auto as hiptlFig
import hc_lib.plots.figures.galaxy_auto as galFig
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

#    hiptlAuto(rlib)
    galaxyAuto(rlib)
    return

# Do this part later
# def histograms(rl):
#     hists = rl
#     for run in hists:
#         for gal_res in run:
#             plt.

def hiptlAuto(rl):
    print('_________ MAKING HIPTL AUTO POWER SPECTRA PLOTS ______\n')
    cc = copy.copy # used often, so just made shortcut
    #rl.printLib()
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
    hiptlFig.redshiftR_spaceC_model(rl, ip, saveDirPath)
     
    ip = cc(baseIncludeProps)
    ip['snapshot'] = 99
    hiptlFig.modelR_spaceC_map(rl, ip, saveDirPath)
    
    ip = cc(baseIncludeProps)
    ip['space'] = 'real'
    hiptlFig.redshiftR_mapC_model(rl, ip, saveDirPath)

    ip = cc(baseIncludeProps)
    ip['map'] = 'mass'
    hiptlFig.redshiftR_modelC_space(rl, ip, saveDirPath)

    # ip = cc(baseIncludeProps)
    # ip['snapshot'] = 99
    # ip['map'] = 'mass'
    # del ip['simname']
    # hiptlFig.modelR_spaceC_simResolution(rl, ip, saveDirPath)
    

    ip = cc(baseIncludeProps)
    ip['map'] = 'mass'
    del ip['axis']
    ip['model'] = 'GD14'
    hiptlFig.redshiftR_spaceC_axis(rl, ip, saveDirPath)
    return

def galaxyAuto(rl):
    # color - red, blue, resolved, all
    # species - stmass, total
    # gal_res - anderson_2df, wolz_eBOSS_LRG, wolz_eBOSS_ELG, wolz_wiggleZ,
    # papastergis_SDSS, diemer
    # color_cut - papastergis_SDSS, wolz_eBOSS_ELG, wolz_eBOSS_LRG, anderson_2df,
    # wolz_wiggleZ, visual_inspection, 0.50, 0.55,0.60, 0.65, 0.70
    print('_________ MAKING GALAXY AUTO POWER SPECTRA PLOTS ______\n')
    cc = copy.copy # used often, so just made shortcut
    # rl.printLib()
    # create directory to save figures in
    saveDirPath = SAVEPATH+'galaxy_auto/'
    if not os.path.isdir(saveDirPath):
        os.mkdir(saveDirPath)
    
    baseIncludeProps = {}
    baseIncludeProps['fieldname'] = 'galaxy'
    baseIncludeProps['simname'] = 'tng100'
    baseIncludeProps['snapshot'] = 99
    baseIncludeProps['axis'] = 0
    baseIncludeProps['grid_resolution'] = 800
    baseIncludeProps['gal_res'] = 'diemer'
    baseIncludeProps['is_auto'] = True
    baseIncludeProps['mas'] = 'CICW'
    baseIncludeProps['color_cut'] = '0.60'
    baseIncludeProps['species'] = 'stmass'
    baseIncludeProps['space'] = 'real'
    baseIncludeProps['color'] = 'resolved'
    ip = cc(baseIncludeProps)
    #ip['color'] = ['red', 'blue', 'resolved']
    del ip['snapshot']
    del ip['space']
    del ip['color']
    galFig.redshiftR_spaceC_color(rl, ip, saveDirPath)
    
    ip = cc(baseIncludeProps)
    #ip['fieldname'] = ['galaxy', 'galaxy_dust']
    #ip['color'] = ['red', 'blue']
    del ip['species']
    del ip['color']
    del ip['fieldname']
    galFig.fieldnameR_colorC_species(rl, ip, saveDirPath)

    ip = cc(baseIncludeProps)
    #ip['fieldname'] = ['galaxy', 'galaxy_dust']
    #ip['color'] = ['red', 'blue']
    del ip['mas']
    del ip['fieldname']
    del ip['color']
    galFig.fieldnameR_colorC_mas(rl, ip, saveDirPath)

    #ip = cc(baseIncludeProps)
    #ip['fieldname'] = ['galaxy', 'galaxy_dust']
    #ip['color'] = ['red', 'blue']
    #ip['color_cut'] = ['0.50', '0.55','0.60', '0.65', '0.70']
    #straight_fig = galFig.fieldnameR_colorC_color_cut(rl, ip)
    #straight_fig.saveFig(saveDirPath, 'fieldname','color','color_cut', 'straight')

    ip = cc(baseIncludeProps)
    #ip['fieldname'] = ['galaxy', 'galaxy_dust']
    #ip['color'] = ['red', 'blue']
    #ip['color_cut'] = ['visual_inspection','0.60', 'anderson_2df', 'papastergis_SDSS']
    del ip['fieldname']
    del ip['color']
    del ip['color_cut']
    obs_fig = galFig.fieldnameR_colorC_color_cut(rl, ip)
    obs_fig.saveFig(saveDirPath, 'fieldname','color','color_cut', 'obs')

    ip = cc(baseIncludeProps)
    del ip['fieldname']
    del ip['color']
    #ip['fieldname'] = ['galaxy', 'galaxy_dust']
    #ip['color'] = ['red', 'blue']
    del ip['snapshot']
    galFig.redshiftR_colorC_fieldname(rl, ip, saveDirPath)
    
    return
main()

