from hc_lib.plots.results import ResultLibrary
import hc_lib.plots.figures.hiptl_auto as hiptlFig
import hc_lib.plots.figures.galaxy_auto as galFig
import hc_lib.plots.figures.hisubhalo_auto as hisubFig
import hc_lib.plots.figures.ptl_auto as ptlFig
import hc_lib.plots.figures.vn_auto as vnFig
import hc_lib.plots.figures.all_auto as autoFig
import hc_lib.plots.figures.HIXgalaxy as HIxgal
import hc_lib.plots.figures.HIXptl as HIxptl
import sys
import os
import copy

sys.argv.pop(0)
SAVEPATH = sys.argv.pop(0)
OUTPATHS = sys.argv


def getBIP():
    baseIncludeProps = {}
    baseIncludeProps['simname'] = 'tng100'
    baseIncludeProps['axis'] = 0
    baseIncludeProps['grid_resolution'] = 800
    baseIncludeProps['is_auto'] = True
    #baseIncludeProps['model'] = 'm_hi_GD14_map'
    #baseIncludeProps['projection'] = 'map'
    baseIncludeProps['snapshot'] = 99
    baseIncludeProps['mas'] = 'CICW'
    baseIncludeProps['space'] = 'real'
    baseIncludeProps['sim_resolution'] = 'high'
    return baseIncludeProps

def main():
    if not os.path.isdir(SAVEPATH):
        os.mkdir(SAVEPATH)
    
    rlib = ResultLibrary()
    for OUTPATH in OUTPATHS:
        rlib.addResults(directory=OUTPATH)
    
    def printlib(pname):
        print(rlib.getVals('pk',pname))

    printlib('fieldname')
    
    #hiptlAuto(rlib)
    galaxyAuto(rlib)
    #hisubhaloAuto(rlib)
    #ptlAuto(rlib)
    #vnAuto(rlib)
    #allAuto(rlib)
    # HI_galaxy_cross_power(rlib)
    # HI_ptl_cross_power(rlib)

    return


def HI_galaxy_cross_power(rl):
    print('_________ MAKING HI-GALAXY CROSS POWER SPECTRA PLOTS ______\n')
    cc = copy.copy # used often, so just made shortcut
    #rl.printLib()
    # create directory to save figures in
    saveDirPath = SAVEPATH+'HIXgalaxy/'
    if not os.path.isdir(saveDirPath):
        os.mkdir(saveDirPath)
    
    bip = getBIP()
    bip['is_auto'] = False
    bip['color'] = 'resolved'
    bip['map'] = 'mass'
    bip['HI_res'] = 'hi'
    bip['gal_res'] = 'diemer'
    bip['color_cut'] = None
    bip['species'] = 'stmass'
    bip['fieldname'] = ['galaxy', 'hisubhalo', 'hiptl', 'vn']
    
    ip = cc(bip)
    del ip['snapshot'], ip['space']
    #HIxgal.redshiftR_spaceC_fieldname_distortion(rl, ip, saveDirPath)
    
    HIxgal.redshiftR_spaceC_fieldname_no_distortion(rl, ip, saveDirPath)
    HIxgal.fieldnameR_spaceC_redshift(rl, ip, saveDirPath)
    HIxgal.redshiftR_fieldnameC_space(rl, ip, saveDirPath)



    return

def HI_ptl_cross_power(rl):
    print('_________ MAKING HI-PTL CROSS POWER SPECTRA PLOTS ______\n')
    cc = copy.copy # used often, so just made shortcut
    #rl.printLib()
    # create directory to save figures in
    saveDirPath = SAVEPATH+'HIXptl/'
    if not os.path.isdir(saveDirPath):
        os.mkdir(saveDirPath)


    bip = getBIP()
    bip['is_auto'] = False
    bip['color'] = 'resolved'
    bip['map'] = 'mass'
    bip['HI_res'] = 'hi'
    bip['gal_res'] = 'diemer'
    bip['color_cut'] = None
    bip['species'] = 'ptl'
    bip['fieldname'] = ['ptl', 'hisubhalo', 'hiptl', 'vn']

    ip = cc(bip)
    del ip['space'], ip['snapshot']
    HIxptl.redshiftR_spaceC_fieldname_no_distortion(rl, ip, saveDirPath)
    HIxptl.redshiftR_spaceC_fieldname_distortion(rl, ip, saveDirPath)
    HIxptl.fieldnameR_spaceC_redshift(rl, ip, saveDirPath)
    HIxptl.redshiftR_fieldnameC_space(rl, ip, saveDirPath)
    return

def hiptlAuto(rl):
    print('_________ MAKING HIPTL AUTO POWER SPECTRA PLOTS ______\n')
    cc = copy.copy # used often, so just made shortcut
    #rl.printLib()
    # create directory to save figures in
    saveDirPath = SAVEPATH+'hiptl_auto/'
    if not os.path.isdir(saveDirPath):
        os.mkdir(saveDirPath)
    
    bip = getBIP()
    bip['fieldname'] = 'hiptl'
    bip['model'] = 'GD14'
    bip['map'] = 'mass'

    ip = cc(bip)
    del ip['snapshot'], ip['space'], ip['model']
    hiptlFig.redshiftR_spaceC_model(rl, ip, saveDirPath)
    
    hiptlFig.modelR_spaceC_redshift(rl, ip, saveDirPath)
    
    hiptlFig.redshiftR_modelC_space(rl, ip, saveDirPath)

    ip = cc(bip)
    del ip['simname'], ip['space'], ip['snapshot']
    hiptlFig.redshiftR_spaceC_box(rl, ip, saveDirPath)

    del ip['sim_resolution']
    hiptlFig.redshiftR_spaceC_simResolution(rl, ip, saveDirPath)
    
    ip = cc(bip)
    del ip['grid_resolution'], ip['space'], ip['snapshot']
    hiptlFig.redshiftR_spaceC_gridResolution(rl, ip, saveDirPath)

    ip = cc(bip)
    del ip['axis'], ip['snapshot'], ip['space']
    hiptlFig.redshiftR_spaceC_axis(rl, ip, saveDirPath)

    ip = cc(bip)
    del ip['model'], ip['snapshot']
    ip['space'] = 'redshift'
    hiptlFig.redshiftR_modelC_2D(rl, ip, saveDirPath)

    ip = cc(bip)
    del ip['axis'], ip['model']
    ip['space'] = 'redshift'
    hiptlFig.axisR_modelC_2D(rl, ip, saveDirPath)

    ip = cc(bip)
    del ip['snapshot'], ip['space']
    hiptlFig.redshiftR_spaceC_slice(rl, ip, saveDirPath)
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
    
    bip = getBIP()
    bip['fieldname'] = 'galaxy'
    bip['color'] = 'resolved'
    bip['color_cut'] = ['0.60', None] #includes both red, blue, resovled
    bip['species'] = 'stmass'
    bip['gal_res'] = 'diemer'


    # make plots with just resolved galaxies
    ip = cc(bip)
    del ip['snapshot']
    del ip['space']
    del ip['color']
    galFig.redshiftR_spaceC_color(rl, ip, saveDirPath)
    
    galFig.redshiftR_colorC_space(rl, ip, saveDirPath)
    
    galFig.colorR_spaceC_redshift(rl, ip, saveDirPath)

    # make plots with everything
    ip['gal_res'] = ['diemer', None]
    flib = galFig.redshiftR_spaceC_color(rl, ip)
    flib.saveFig(saveDirPath, 'redshift', 'space', 'color', 'withall')
    flib = galFig.redshiftR_colorC_space(rl, ip)
    flib.saveFig(saveDirPath, 'redshift', 'color', 'space', 'withall')
    flib = galFig.colorR_spaceC_redshift(rl, ip)
    flib.saveFig(saveDirPath, 'color', 'space', 'redshift', 'withall')



    
    ip = cc(bip)
    del ip['species']
    del ip['color']
    del ip['space']
    galFig.spaceR_colorC_species(rl, ip, saveDirPath)

    ip = cc(bip)
    del ip['fieldname']
    del ip['color']
    del ip['snapshot']
    galFig.redshiftR_colorC_fieldname(rl, ip, saveDirPath)
    

    ip = cc(bip)
    del ip['axis']
    del ip['color']
    ip['space'] = 'redshift'
    del ip['snapshot']
    flib = galFig.redshiftR_colorC_axis(rl, ip)
    flib.saveFig(saveDirPath, 'redshift', 'color', 'axis', 'redshift_axis_test')

    ip = cc(bip)
    ip['fieldname'] = ['galaxy', 'galaxy_dust']
    del ip['color']
    ip['color_cut'] = ['visual_inspection', '0.60', '0.55', '0.50', '0.65', '0.70']
    galFig.fieldnameR_colorC_color_cut(rl, ip, saveDirPath)

    ip = cc(bip)
    del ip['axis']
    del ip['color']
    ip['fieldname'] = 'galaxy_dust'
    del ip['snapshot']
    ip['space'] = 'redshift'
    flib = galFig.redshiftR_colorC_axis(rl, ip)

    flib.saveFig(saveDirPath, 'redshift', 'color', 'axis', 'dust_rss_axis_test')

    ip['space'] = 'real'
    flib = galFig.redshiftR_colorC_axis(rl, ip)
    flib.saveFig(saveDirPath, 'redshift', 'color', 'axis', 'dust_real_axis_test')
    ip = cc(bip)
    del ip['color']
    del ip['snapshot']
    ip['space'] = 'redshift'
    galFig.redshiftR_colorC_2D(rl, ip, saveDirPath)

    ip = cc(bip)
    del ip['axis']
    del ip['color']
    ip['space'] = 'redshift'
    galFig.axisR_colorC_2D(rl, ip, saveDirPath)
    
    ip = {}
    ip['fieldname'] = ['galaxy', 'galaxy_dust']
    galFig.make_histograms(rl, ip, saveDirPath)
    return

def hisubhaloAuto(rl):
    print('_________ MAKING HISUBHALO AUTO POWER SPECTRA PLOTS ______\n')
    cc = copy.copy # used often, so just made shortcut
    #rl.printLib()
    # create directory to save figures in
    saveDirPath = SAVEPATH+'hisubhalo_auto/'
    if not os.path.isdir(saveDirPath):
        os.mkdir(saveDirPath)
    
    bip = getBIP()
    bip['HI_res'] = 'hi' # needs fixing later
    bip['projection'] = 'hi' # needs fixing later
    bip['model'] = 'm_hi_GD14_map'
    bip['fieldname'] = 'hisubhalo'
    
    #rl.printLib({'fieldname':'hisubhalo'}, 'pk')

    ip = cc(bip)
    del ip['snapshot']
    del ip['model'], ip['projection']
    del ip['space']
    hisubFig.redshiftR_spaceC_model(rl, ip, saveDirPath)
    
    hisubFig.modelR_spaceC_redshift(rl, ip, saveDirPath)
    
    hisubFig.redshiftR_modelC_space(rl, ip, saveDirPath)

    ip = cc(bip)
    del ip['simname'], ip['snapshot'], ip['space']
    hisubFig.redshiftR_spaceC_box(rl, ip, saveDirPath)

    ip = cc(bip)
    del ip['simname'], ip['snapshot'], ip['space'], ip['sim_resolution']
    hisubFig.redshiftR_spaceC_simResolution(rl, ip, saveDirPath)
    
    ip = cc(bip)
    del ip['snapshot'], ip['space'], ip['grid_resolution']
    hisubFig.redshiftR_spaceC_gridResolution(rl, ip, saveDirPath)

    ip = cc(bip)
    del ip['axis'], ip['snapshot'], ip['space']
    hisubFig.redshiftR_spaceC_axis(rl, ip, saveDirPath)

    ip=cc(bip)
    del ip['snapshot'], ip['model'], ip['projection']
    ip['space'] = 'redshift'
    hisubFig.redshiftR_modelC_2D(rl, ip, saveDirPath)

    ip = cc(bip)
    del ip['axis'], ip['model'], ip['projection']
    ip['space']= 'redshift'
    hisubFig.axisR_modelC_2D(rl, ip, saveDirPath)

    return

def ptlAuto(rl):
    print('_________ MAKING PARTICLE AUTO POWER SPECTRA PLOTS ______\n')
    cc = copy.copy # used often, so just made shortcut
    # rl.printLib()
    # create directory to save figures in
    saveDirPath = SAVEPATH+'ptl_auto/'
    if not os.path.isdir(saveDirPath):
        os.mkdir(saveDirPath)
    
    bip = getBIP()
    bip['fieldname'] = 'ptl'
    bip['species'] = 'ptl'
    


    ip = cc(bip)
    del ip['snapshot'], ip['space'], ip['species']
    ptlFig.redshiftR_spaceC_species(rl, ip, saveDirPath)

    ptlFig.redshiftR_speciesC_space(rl, ip, saveDirPath)

    ptlFig.speciesR_spaceC_redshift(rl, ip, saveDirPath)

    ip = cc(bip)
    del ip['species'], ip['space']
    ptlFig.speciesR_spaceC_slice(rl, ip, saveDirPath)

    ip = cc(bip)
    del ip['axis'], ip['species']
    ip['space'] = 'redshift'
    ptlFig.axisR_speciesC_2D(rl, ip, saveDirPath)

    ip = cc(bip)
    del ip['snapshot'], ip['species']
    ip['space'] = 'redshift'
    ptlFig.redshiftR_speciesC_2D(rl, ip, saveDirPath)

    return

def vnAuto(rl):
    print('_________ MAKING VN18-PARTICLE AUTO POWER SPECTRA PLOTS ______\n')
    cc = copy.copy # used often, so just made shortcut
    # rl.printLib()
    # create directory to save figures in
    saveDirPath = SAVEPATH+'vn_auto/'
    if not os.path.isdir(saveDirPath):
        os.mkdir(saveDirPath)
    
    bip =getBIP()
    bip['map'] = 'mass'
    bip['fieldname'] = 'vn'
    ip = cc(bip)
    del ip['snapshot'], ip['space']
    vnFig.fieldnameR_redshiftC_space(rl, ip, saveDirPath)
    vnFig.fieldnameR_spaceC_redshift(rl, ip, saveDirPath)
    
    return

def allAuto(rl):
    print('_________ MAKING ALL AUTO POWER SPECTRA PLOTS ______\n')
    cc = copy.copy # used often, so just made shortcut
    # rl.printLib()
    # create directory to save figures in
    saveDirPath = SAVEPATH+'all_auto/'
    if not os.path.isdir(saveDirPath):
        os.mkdir(saveDirPath)

    bip = getBIP()

    # HI auto power spectra
    ip = cc(bip)
    del ip['snapshot'], ip['space']
    ip['fieldname'] = ['vn', 'hiptl', 'hisubhalo']
     
    autoFig.redshiftR_spaceC_fieldname_distortion(rl, ip, saveDirPath)
    autoFig.redshiftR_spaceC_fieldname_no_distortion(rl, ip, saveDirPath)

    
    ip = cc(bip)
    del ip['space']
    ip['fieldname'] = ['vn', 'ptl','hiptl', 'hisubhalo', 'galaxy']
    ip['species'] = ['stmass', 'gas']
    ip['model'] = ['GD14', 'f_hi_GD14_map']
    ip['color'] = ['resolved']
    ip['map'] = ['mass']
    #autoFig.fieldnameR_spaceC_slice(rl, ip, saveDirPath)

    ip = cc(bip)
    del ip['axis'], ip['snapshot']
    ip['fieldname'] = ['vn', 'ptl','hiptl', 'hisubhalo', 'galaxy']
    ip['species'] = ['stmass', 'gas']
    ip['model'] = ['GD14', 'f_hi_GD14_map']
    ip['color'] = ['resolved']
    ip['map'] = ['mass']
    autoFig.fieldnameR_redshiftC_axis(rl, ip, saveDirPath)


main()
