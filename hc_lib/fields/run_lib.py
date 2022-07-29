import numpy as np

def galaxyRuns():
    runs = ['fiducial', 'alt_MAS', 'axis_test', 'colordef_test',
            'bins_thresholds', 'species_test', 'all_test', 'centrals_test']
    return runs

def hisubRuns():
    runs = ['fiducial', 'alt_MAS', 'bins_thresholds', 'centrals_test']
    return runs

def galaxyColorMasks(photo, stmass, color_cut):
    if color_cut == 'visual_inspection':
        x = stmass
        y = photo['gr']
        red_mask = y > 0.65 + 0.02 * (np.log10(x) - 10.28)
        blue_mask = np.invert(red_mask)
    elif color_cut == 'papastergis_SDSS':
        x = photo['r']
        y = photo['gi']
        red_mask = y > 0.0571 * (x + 24) + 1.25
        blue_mask = y < 0.0571 * (x + 24) + 1.1
        # excludes green valley galaxies in between these two lines
    elif color_cut == 'wolz_eBOSS_ELG':
        
        blue_mask = np.ones_like(stmass, dtype=bool)
        red_mask = np.zeros_like(stmass, dtype=bool)

    elif color_cut == 'wolz_eBOSS_LRG':
        blue_mask = np.zeros_like(stmass, dtype=bool)
        red_mask = np.ones_like(stmass, dtype=bool)
    
    elif color_cut == 'wolz_wiggleZ':
        blue_mask = np.ones_like(stmass, dtype=bool)
        red_mask = np.zeros_like(stmass, dtype=bool)

    elif color_cut == 'anderson_2df':
        x = photo['b_j']
        y = photo['r_f']
        red_mask = x - y > 1.07
        blue_mask = np.invert(red_mask)
    else:
        y = photo['gr']
        x = float(color_cut)
        red_mask = y > x
        blue_mask = np.invert(red_mask)
    return blue_mask, red_mask
    

def galaxyResolvedMask(stmass, gasmass, photo, res_dict):
    ################ HELPER METHODS #############################
    def gr_elg():
        mn = -0.068*photo['rz']+0.457
        mx = 0.112*photo['rz']+1.901

        return (photo['gr'] > mn) & (photo['gr'] < mx)
    
    def rz_elg():
        mn = 0.218*photo['gr'] + 0.571
        mx = -0.555*photo['gr']+1.901

        return (photo['rz'] > mn) & (photo['rz'] < mx)
    
    ##############################################################


    resolved = np.ones_like(stmass, dtype=bool)
    for r in res_dict:
        if r == 'stmass':
            t = res_dict[r]
            stmass_resolved = (stmass >= t[0]) & (stmass < t[1])
            resolved *= stmass_resolved
        elif r == 'gas':
            t = res_dict[r]
            gas_resolved = (gasmass >= t[0]) & (gasmass < t[1])
            resolved *= gas_resolved
        else:
            t = res_dict[r]
            if t == 'gr_elg':
                photo_resolved = gr_elg()
            elif t == 'rz_elg':
                photo_resolved = rz_elg()
            else:
                photo_resolved = (photo[r] > t[0]) & (photo[r] < t[1])
            resolved *= photo_resolved
    
    return resolved


def galaxyResDefs(simname):
    # taken from Benedikt's cuts 2018, table 1 (in solar masses)
    if simname in ['orig', 'tng100']:
        Mstar_min = 2E8
        Mgas_min = 2E8
    elif simname == 'tng300':
        Mstar_min = 2.2E9
        Mgas_min = 2.2E9

    elif simname == 'tng100-2':
        Mstar_min = 1.1E9
        Mgas_min = 1.1E9
    elif simname == 'tng100-3':
        Mstar_min = 9E9
        Mgas_min = 9E9
    
    # papastergis: z=.0023-0.05
    # wolz: z=0.6-1.0
    # anderson: z ~ 0

    # the different definitions of what makes a galaxy resolved
    galaxy_min_resolution = {}
    # from papastergis 2013, minimum for galaxies is r-band lum of -17 mag
    galaxy_min_resolution['papastergis_SDSS'] = {'r':(-np.inf,-17)}
    # papastergis makes an additional cut (i-z) > -0.25, but states that
    # this cut eliminates a small number of misidentified galaxies by the 
    # SDSS pipeline
    # resolution to match hisubhalo
    galaxy_min_resolution['diemer'] = {'stmass':(Mstar_min, np.inf)}

    # wigglez isn't a good comparison, TNG doesn't have any equivalent UV
    # filters and wigglez has poor r definition (from wolz)
    #galaxy_min_resolution['wolz_wiggleZ'] = {'r':(20,22)}
    
    # eBOSS Emission line galaxies
    #galaxy_min_resolution['wolz_eBOSS_ELG'] = {'g':(21.825, 22.825), 'gr':'gr_elg',
    #'rz':'rz_elg'}
    # since gr and rz depend on other values, use strings to indicate a method
    # to use in the resolution definition
    #galaxy_min_resolution['wolz_eBOSS_LRG'] = {'i':(19.9,21.8), 'z':(-np.inf, 19.95),
    #            'ri':(0.98, np.inf)}
    # I still need to check if there is an equivalent band for IRACI in TNG

    #galaxy_min_resolution['anderson_2df'] = {'b_j':(-np.inf, 19.45), 'r_f':(-np.inf, 21)}

    # calculate the magnitude orders to get threshold/bin tests
    oom = int(np.log10(Mstar_min))

    galaxy_min_resolution['low-threshold'] = {'stmass':(10**(oom+1), np.inf)}
    galaxy_min_resolution['mid-threshold'] = {'stmass':(10**(oom+2), np.inf)}
    galaxy_min_resolution['high-threshold'] = {'stmass':(10**(oom+3), np.inf)}
    galaxy_min_resolution['low-bin'] = {'stmass':(Mstar_min, 10**(oom+1))}
    galaxy_min_resolution['mid-bin'] = {'stmass':(10**(oom+1), 10**(oom+2))}
    galaxy_min_resolution['high-bin'] = {'stmass':(10**(oom+2), 10**(oom+3))}

    galaxy_min_resolution['tng100-2'] = {'stmass':(1.1e9, np.inf)}
    galaxy_min_resolution['tng300'] = {'stmass':(5e10, np.inf)}
    return galaxy_min_resolution

def galaxyColorDefs():
    obs = galaxyObsColorDefs()
    implemented_color_defs = ['visual_inspection', '0.50', '0.55', 
            '0.60', '0.65', '0.70']
    
    #implemented_color_defs.extend(obs)
    return implemented_color_defs

def galaxyObsColorDefs():
    return ['papastergis_SDSS', 'wolz_eBOSS_ELG', 'wolz_eBOSS_LRG', 'anderson_2df',
            'wolz_wiggleZ']

def getMolFracModelsPtl():
    return ['GD14', 'GK11', 'S14', 'K13']

def HIResolutionDefinitions(simname):
    # taken from Pillepich et al 2018, table 1 (in solar masses)
    mean_baryon_cell = {'tng100':1.4e6, 'tng100-2':11.2e6, 'tng100-3':89.2e6,
            'tng300':11e6, 'tng300-2':88e6, 'tng300-3':703e6}
    thres = mean_baryon_cell[simname] * 200

    res_defs = {}
    #res_defs['papastergis_ALFALFA'] = {'HI':(10**7.5, np.inf)} 
    res_defs['diemer'] = {'HI':(0, np.inf)} # by default, already implemented on data
    res_defs['low-threshold'] = {'HI':(10**7, np.inf)}
    res_defs['mid-threshold'] = {'HI':(10**8, np.inf)}
    res_defs['high-threshold'] = {'HI':(10**9, np.inf)}
    
    # res_defs['lowest-bin'] = {'HI':(-np.inf, 10**7)}
    res_defs['low-bin'] = {'HI':(10**7,10**8)}
    res_defs['mid-bin'] = {'HI':(10**8,10**9)}
    res_defs['high-bin'] = {'HI':(10**9,np.inf)}
    # there is a linewidths restriction, unsure how to approach that in papastergis
    # wolz is intensity map so no minimum threshold

    res_defs['tng100-2'] = {'stmass':(1e9, np.inf), 'gas':(1e9, np.inf)}
    res_defs['tng300'] = {'stmass':(5e10, np.inf), 'gas':(5e9, np.inf)}
    return res_defs
    

def getMolFracModelsGalHI():
    """
    Returns a list of the molecular fraction models provided by Diemer+ 2018,
    specifically the ones that respond to the subhalo catalog.
    """
    models = ['GD14','GK11','K13','S14']
    proj = ['map','vol']
    modelnames = []
    for m in models:
        for p in proj:
            modelnames.append('m_hi_%s_%s'%(m,p))
    modelnames.append('m_hi_L08_map')
    return modelnames

    
def getMolFracModelsGalH2():
    """
    Returns a list of the molecular fraction models provided by Diemer+ 2018,
    specifically the ones that correspond to the subhalo catalog.
    """
    models = ['GD14','GK11','K13','S14']
    proj = ['map','vol']
    gridnames = []
    for m in models:
        for p in proj:
            gridnames.append('m_h2_%s_%s'%(m,p))
    gridnames.append('m_h2_L08_map')
    return gridnames
