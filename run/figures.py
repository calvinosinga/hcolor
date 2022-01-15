from hc_lib.plots.results import ResultLibrary
import hc_lib.plots.figures.hiptl_auto as hiptlFig
import hc_lib.plots.figures.galaxy_auto as galFig
import hc_lib.plots.figures.hisubhalo_auto as hisubFig
import hc_lib.plots.figures.ptl_auto as ptlFig
import hc_lib.plots.figures.vn_auto as vnFig
import hc_lib.plots.figures.HI_auto as HIFig
import hc_lib.plots.figures.HIXgalaxy as HIxgal
import hc_lib.plots.figures.HIXptl as HIxptl
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
    
    def printlib(pname):
        print(rlib.getVals('pk',pname))

    printlib('fieldname')
    
    # hiptlAuto(rlib)
    galaxyAuto(rlib)
    # hisubhaloAuto(rlib)
    # ptlAuto(rlib)
    # vnAuto(rlib)
    # HIAuto(rlib)
    # HI_galaxy_cross_power(rlib)
    # HI_ptl_cross_power(rlib)

    return

def HIAuto(rl):
    print('_________ MAKING HI AUTO POWER SPECTRA PLOTS ______\n')
    cc = copy.copy # used often, so just made shortcut
    # rl.printLib()
    # create directory to save figures in
    saveDirPath = SAVEPATH+'HI_auto/'
    if not os.path.isdir(saveDirPath):
        os.mkdir(saveDirPath)
    
    baseIncludeProps = {}
    baseIncludeProps['simname'] = 'tng100'
    baseIncludeProps['snapshot'] = 99
    baseIncludeProps['axis'] = 0
    baseIncludeProps['grid_resolution'] = 800
    baseIncludeProps['is_auto'] = True
    baseIncludeProps['is_hydrogen'] = True

    ip = cc(baseIncludeProps)
    HIFig.redshiftR_spaceC_fieldname(rl, ip, saveDirPath)
    return

def HI_galaxy_cross_power(rl):
    print('_________ MAKING HI-GALAXY CROSS POWER SPECTRA PLOTS ______\n')
    cc = copy.copy # used often, so just made shortcut
    #rl.printLib()
    # create directory to save figures in
    saveDirPath = SAVEPATH+'HIXgalaxy/'
    if not os.path.isdir(saveDirPath):
        os.mkdir(saveDirPath)
    
    baseIncludeProps = {}
    baseIncludeProps['fieldname'] = 'galaxy'
    baseIncludeProps['simname'] = 'tng100'
    baseIncludeProps['axis'] = 0
    baseIncludeProps['grid_resolution'] = 800
    baseIncludeProps['is_auto'] = False

    ip = cc(baseIncludeProps)
    HIxgal.redshiftR_spaceC_fieldname(rl, ip, saveDirPath)
    return

def HI_ptl_cross_power(rl):
    print('_________ MAKING HI-PTL CROSS POWER SPECTRA PLOTS ______\n')
    cc = copy.copy # used often, so just made shortcut
    #rl.printLib()
    # create directory to save figures in
    saveDirPath = SAVEPATH+'HIXptl/'
    if not os.path.isdir(saveDirPath):
        os.mkdir(saveDirPath)
    
    baseIncludeProps = {}
    baseIncludeProps['fieldname'] = 'ptl'
    baseIncludeProps['simname'] = 'tng100'
    baseIncludeProps['axis'] = 0
    baseIncludeProps['grid_resolution'] = 800
    baseIncludeProps['is_auto'] = False

    ip = cc(baseIncludeProps)
    HIxptl.redshiftR_spaceC_fieldname(rl, ip, saveDirPath)
    return

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
    ip['map'] = 'mass'
    hiptlFig.redshiftR_modelC_space(rl, ip, saveDirPath)

    ip = cc(baseIncludeProps)
    ip['snapshot'] = 99
    hiptlFig.mapR_spaceC_model(rl, ip, saveDirPath)


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

    ip = cc(baseIncludeProps)
    ip['model'] = 'GD14'
    ip['snapshot'] = 99
    hiptlFig.mapR_spaceC_2D(rl, ip, saveDirPath)

    ip = cc(baseIncludeProps)
    ip['model'] = 'GD14'
    ip['map'] = 'mass'
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

    # make plots with just resolved galaxies
    ip = cc(baseIncludeProps)
    del ip['snapshot']
    del ip['space']
    del ip['color']
    ip['color_cut'] = ['0.60', None]
    galFig.redshiftR_spaceC_color(rl, ip, saveDirPath)
    
    galFig.redshiftR_colorC_space(rl, ip, saveDirPath)
    
    # make plots with everything
    ip['gal_res'] = ['diemer', None]
    flib = galFig.redshiftR_spaceC_color(rl, ip)
    flib.saveFig(saveDirPath, 'redshift', 'space', 'color', '_withall')
    flib = galFig.redshiftR_colorC_space(rl, ip)
    flib.saveFig(saveDirPath, 'redshift', 'color', 'space', '_withall')


    ip = cc(baseIncludeProps)
    del ip['species']
    del ip['color']
    ip['color_cut'] = ['0.60', None]
    del ip['space']
    galFig.spaceR_colorC_species(rl, ip, saveDirPath)

    ip = cc(baseIncludeProps)
    del ip['fieldname']
    del ip['color']
    del ip['snapshot']
    galFig.redshiftR_colorC_fieldname(rl, ip, saveDirPath)
    

    ip = cc(baseIncludeProps)
    del ip['axis']
    del ip['color']
    del ip['space']
    galFig.fieldnameR_colorC_axis(rl, ip, saveDirPath)

    ip = cc(baseIncludeProps)
    del ip['color']
    ip['color_cut'] = [None, '0.60']
    del ip['snapshot']

    galFig.colorR_redshiftC_2D(rl, ip, saveDirPath)

    ip = cc(baseIncludeProps)
    del ip['axis']
    ip['color_cut'] = ['0.60', None]
    del ip['color']
    galFig.axisR_colorC_2D(rl, ip, saveDirPath)

    galFig.make_histograms(rl, saveDirPath)
    return

def hisubhaloAuto(rl):
    print('_________ MAKING D18-SUBHALO AUTO POWER SPECTRA PLOTS ______\n')
    cc = copy.copy # used often, so just made shortcut
    # rl.printLib()
    # create directory to save figures in
    saveDirPath = SAVEPATH+'hisubhalo_auto/'
    if not os.path.isdir(saveDirPath):
        os.mkdir(saveDirPath)
    
    baseIncludeProps = {}
    baseIncludeProps['fieldname'] = 'hisubhalo'
    baseIncludeProps['simname'] = 'tng100'
    baseIncludeProps['snapshot'] = 99
    baseIncludeProps['axis'] = 0
    baseIncludeProps['grid_resolution'] = 800
    #baseIncludeProps['HI_res'] = 'diemer'
    baseIncludeProps['is_auto'] = True
    baseIncludeProps['space'] = 'real'
    baseIncludeProps['mas']='CICW'
    
    ip = {}
    ip['fieldname'] = 'hisubhalo'
    #rl.printLib(ip, 'pk')

    ip = cc(baseIncludeProps)
    del ip['space']
    #del ip['HI_res']
    #hisubFig.modelR_spaceC_HI_res(rl, ip, saveDirPath)

    ip = cc(baseIncludeProps)
    del ip['space']
    del ip['mas']
    hisubFig.modelR_spaceC_mas(rl, ip, saveDirPath)

    ip = cc(baseIncludeProps)
    del ip['snapshot']
    del ip['space']
    hisubFig.redshiftR_spaceC_model(rl, ip, saveDirPath)
    return

def ptlAuto(rl):
    print('_________ MAKING PARTICLE AUTO POWER SPECTRA PLOTS ______\n')
    cc = copy.copy # used often, so just made shortcut
    # rl.printLib()
    # create directory to save figures in
    saveDirPath = SAVEPATH+'ptl_auto/'
    if not os.path.isdir(saveDirPath):
        os.mkdir(saveDirPath)
    
    baseIncludeProps = {}
    baseIncludeProps['fieldname'] = 'ptl'
    baseIncludeProps['simname'] = 'tng100'
    #baseIncludeProps['snapshot'] = 99
    baseIncludeProps['axis'] = 0
    baseIncludeProps['grid_resolution'] = 800
    #baseIncludeProps['species'] = 'ptl'
    baseIncludeProps['is_auto'] = True
    baseIncludeProps['mas'] = 'CICW'
    # baseIncludeProps['space'] = 'real'


    ip = cc(baseIncludeProps)
    ptlFig.redshiftR_spaceC_species(rl, ip, saveDirPath)

    return

def vnAuto(rl):
    print('_________ MAKING VN18-PARTICLE AUTO POWER SPECTRA PLOTS ______\n')
    cc = copy.copy # used often, so just made shortcut
    # rl.printLib()
    # create directory to save figures in
    saveDirPath = SAVEPATH+'vn_auto/'
    if not os.path.isdir(saveDirPath):
        os.mkdir(saveDirPath)
    
    baseIncludeProps = {}
    baseIncludeProps['fieldname'] = 'vn'
    baseIncludeProps['simname'] = 'tng100'
    #baseIncludeProps['snapshot'] = 99
    baseIncludeProps['axis'] = 0
    baseIncludeProps['grid_resolution'] = 800
    #baseIncludeProps['species'] = 'ptl'
    baseIncludeProps['is_auto'] = True
    baseIncludeProps['mas'] = 'CICW'
    # baseIncludeProps['space'] = 'real'


    ip = cc(baseIncludeProps)
    vnFig.redshiftR_fieldnameC_space(rl, ip, saveDirPath)
    # vnFig.redshiftR_mapC_space(rl, ip, saveDirPath)

    # vnFig.redshiftR_spaceC_map(rl, ip, saveDirPath)
    
    return


main()

