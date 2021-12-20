import copy
from hc_lib.fields.galaxy import getObservationalDefinitions as galaxyObsResDef
from hc_lib.fields.hisubhalo import getMolFracModelsGalHI as galMolFracModelsHI
from hc_lib.fields.hisubhalo import getMolFracModelsGalH2 as galMolFracModelsH2


class grid_props():
    
    def __init__(self, mas, field, space, other_props,
                compute_xi = True, compute_slice = True):
        self.props = {}
        self.props['mas'] = mas
        self.props['fieldname'] = field
        self.props['space'] = space
        self.props['compute_xi'] = compute_xi
        self.props['compute_slice'] = compute_slice
        self.props.update(other_props)
        return

    def getH5DsetName(self):
        out = ''
        
        for k, v in self.props.items():
            compute_input = k == 'compute_slice' or k == 'compute_xi'
            if not v is None and not compute_input:
                out+= "%s_"%v
        
        out = out[:-1]
        return out

    def isIncluded(self):
        """
        Determines if the grid with the given properties should be included
        in the analysis.
        """
        return True

    def saveProps(self, h5set):
        for k,v in self.props.items():
            if not v is None:
                h5set.attrs[k] = v
        return
    
    @classmethod
    def loadProps(cls, dct):
        temp = copy.copy(dict(dct))
        return grid_props(temp.pop('mas'), 
                temp.pop("fieldname"), temp.pop('space'), temp)
    
    def isCompatible(self, other):
        """
        Reports if two grids are compatible for cross-correlation
        """
        mas = self.props['mas'] == other.props['mas']
        space = self.props['space'] == other.props['space']
        return mas and space

###############################################################################################

class galaxy_grid_props(grid_props):
    """
    Since each galaxy field has an enormous number of grids, this contains the data
    for one grid
    """
    def __init__(self, mas, field, space, color, species, 
                gal_resolution_def, color_cut):
        other = {}
        lst = [color, species, gal_resolution_def, color_cut]
        keys = ['color', 'species', 'gal_res','color_cut']
        for i in range(len(lst)):
            other[keys[i]] = lst[i]

        super().__init__(mas, field, space, other)

        return
    

    def isCompatible(self, other):
        op = other.props
        sp = self.props

        # for galaxyXgalaxy
        if op['fieldname'] == sp['fieldname']:
            mas_match = op['mas'] == sp['mas']
            stmass_or_total = op['species'] == sp['species']
            resdef_match = op['gal_res'] == sp['gal_res'] and op['gal_res'] == 'diemer'
            coldef_match = op['color_cut'] == sp['color_cut'] and sp['color_cut'] == '0.60'
            space_match = op['space'] == sp['space']
            return mas_match and stmass_or_total and resdef_match and coldef_match and space_match
        
        # hiptlXgalaxy handled by hiptl
        
        # hisubhaloXgalaxy handled by hisubhalo

        # vnXgalaxy handled by vn

        return True

    def isIncluded(self):

        def test(cds, mts, schts):
            cdtest = self.props['color_cut'] in cds
            mtest = self.props['species'] in mts
            mastest = self.props['mas'] in schts
            return cdtest and mtest and mastest
        

        if self.props['gal_res'] == 'papastergis_SDSS':
            cds = ['papastergis_SDSS']
            ms = ['stmass']
            schts = ['CIC']
            return test(cds, ms, schts)
        
        elif self.props['gal_res'] == 'wolz_wiggleZ':
            cds = ['wolz_wiggleZ']
            ms = ['stmass']
            schts = ['CIC']
            return test(cds, ms, schts) and self.props['color'] == 'red'
        
        elif self.props['gal_res'] == 'wolz_eBOSS_ELG':
            cds = ['wolz_eBOSS_ELG']
            ms = ['stmass']
            schts = ['CIC']
            return test(cds, ms, schts) and self.props['color'] == 'blue'

        elif self.props['gal_res'] == 'wolz_eBOSS_LRG':
            cds = ['wolz_eBOSS_LRG']
            ms = ['stmass']
            schts = ['CIC']
            return test(cds, ms, schts) and self.props['color'] == 'red'

        elif self.props['gal_res'] == 'anderson_2df':
            cds = ['anderson_2df']
            ms = ['stmass']
            schts = ['CIC']
            return test(cds, ms, schts)

        # everything that isn't a color definition associated with an observation is fine
        elif self.props['gal_res'] == 'diemer':
            obs_color_cuts = galaxyObsResDef()
            coldef_is_compatible = not (self.props['color_cut'] in obs_color_cuts)
            # CIC between stmass and all mass should be the same - removing redundancy
            is_CICW = self.props['mas'] == 'CICW'
            is_CIC_and_stmass = self.props['mas'] == 'CIC' and self.props['species'] == 'stmass'

            return coldef_is_compatible and (is_CICW or is_CIC_and_stmass)

        # if this is gridprop obj for resolved, then
        elif self.props['color'] == 'resolved':
            # removing redundancy in CIC with both kinds of mass
            is_CICW = self.props['mas'] == 'CICW'
            is_CIC_and_stmass = self.props['mas'] == 'CIC' and self.props['species'] == 'stmass'
            return is_CICW or is_CIC_and_stmass
        
        elif self.props['color'] == 'all':
            is_CICW = self.props['mas'] == 'CICW'
            is_CIC_and_stmass = self.props['mas'] == 'CIC' and self.props['species'] == 'stmass'
            return is_CICW or is_CIC_and_stmass
        return False

############################################################################################################

class hiptl_grid_props(grid_props):

    def __init__(self, mas, field, space, model, mass_or_temp = None, nH = None):
        other = {}
        other['map'] = mass_or_temp
        other['model'] = model
        if not nH is None:
            self.nH_bin = nH
            nH_str = str(nH)
            other['nH_bin'] = nH_str
        else:
            other['nH_bin'] = nH
        super().__init__(mas, field, space, other)
        return
    
    def isCompatible(self, other):
        sp = self.props
        op = other.props

        # hiptl/h2ptlXgalaxy/galaxy_dust
        if 'galaxy' in op['fieldname']:
            # for comparisons to Anderson and Wolz -> stmass/resdef is eBOSS, wiggleZ, 2df
            if 'temp' == sp['map']:
                obs_defs = galaxyObsResDef()
                obs_defs.remove('papastergis_SDSS')
                match_obs = op['gal_res'] in obs_defs and op['color_cut'] in obs_defs
                return match_obs
            
            # if a mass map, it is either diemer
            elif op['gal_res'] == 'diemer':
                # the important color definitions
                cols = ['0.60', '0.55', '0.65', 'visual_inspection']

                # also include resolved
                is_resolved = op['color'] == 'resolved'

                return op['color_cut'] in cols or is_resolved
            
            # ignore all papa resdefs -> hisubhalo is more comparable
            elif op['gal_res'] == 'papa':
                return False
            
            # if all = color, then include
            elif op['color'] == 'all':
                return True

        # hiptlXptl
        else:
            # include if mass map, not temp map
            return sp['map'] == 'mass'

############################################################################################################

class hisubhalo_grid_props(grid_props):

    def __init__(self, mas, field, space, model, HI_res):
        other = {}
        other['model'] = model
        
        other['HI_res'] = HI_res
        super().__init__(mas, field, space, other)
    
    def isIncluded(self):
        def test(schts):
            mastest = self.props['mas'] in schts
            return mastest
            
        sp = self.props
        if sp['HI_res'] == 'papastergis_ALFALFA':
            mas = ['CIC']
            return test(mas) and sp['fieldname'] == 'hisubhalo'

        return True
    
    def setupGrids(self, outfile):
        return super().setupGrids(outfile)
    
    def isCompatible(self, other):
        sp = self.props
        op = other.props
        # hisubhaloXgalaxy
        if 'galaxy' in op['fieldname']:
            # if both have papa resolution definition, include only hisubhalo
            if op['gal_res'] == 'papastergis_SDSS':
                return sp['HI_res'] == 'papastergis_ALFALFA'
            
            # if diemer resdef, include certain color definitions and resolved definition
            elif op['gal_res'] == 'diemer':
                cdefs = ['0.55','0.60','0.65', 'visual_inspection']
                is_resolved = op['color'] == 'resolved'
                return op['color_cut'] in cdefs or is_resolved
            
            # if all galaxies, also include
            elif op['color'] == 'all':
                return True
            
            return False
        
        elif op['fieldname'] == 'ptl':
            if sp['fieldname'] == 'hisubhalo':
                models = galMolFracModelsHI
            elif sp['fieldname'] == 'h2subhalo':
                models = galMolFracModelsH2
            
            return sp['model'] == models[0]
        return True

#############################################################################################################

class ptl_grid_props(grid_props):
    
    def __init__(self, mas, field, space, species):
        other = {'species':species}
        super().__init__(mas, field, space, other)
        return

################################################################################################################

class vn_grid_props(grid_props):
    def __init__(self, mas, field, space, mass_or_temp):
        other = {}
        other['map'] = mass_or_temp

        super().__init__(mas, field, space, other)
    
    def isCompatible(self, other):
        sp = self.props
        op = other.props

        # vnXgalaxy 
        if 'galaxy' in op['fieldname']:
            # for comparisons to Anderson and Wolz -> stmass/resdef is eBOSS, wiggleZ, 2df
            if 'temp' == sp['map']:
                obs = galaxyObsResDef()
                obs.remove('papastergis_SDSS')
                obs_match = op['gal_res'] in obs and op['color_cut'] in obs
                return obs_match
            
            # if a mass map, it is either diemer or papa
            elif op['gal_res'] == 'diemer':
                # the important color definitions
                cols = ['0.60', '0.55', '0.65', 'visual_inspection']

                # also include resolved
                is_resolved = op['color'] == 'resolved'

                return op['color_cut'] in cols or is_resolved
            
            # ignore all papa resdefs -> hisubhalo is more comparable
            elif op['gal_res'] == 'papastergis_SDSS':
                return False
            
            # if all = base, then include
            elif op['color'] == 'all':
                return True

        # vnXptl
        else:
            return sp['map'] == 'mass'