import copy
import hc_lib.fields.run_lib as rl


class grid_props():
    
    def __init__(self, mas, field, space, other_props,
                compute_xi = False, compute_slice = True):
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
        fn = temp['fieldname']

        if fn == 'galaxy' or fn == 'galaxy_dust':
            return galaxy_grid_props.loadProps(temp)

        elif fn == 'hiptl' or fn == 'h2ptl':
            return hiptl_grid_props.loadProps(temp)
        
        elif fn == 'hisubhalo' or fn == 'h2subhalo':
            return hisubhalo_grid_props.loadProps(temp)
        
        elif fn == 'ptl':
            return ptl_grid_props.loadProps(temp)
        
        elif fn == 'vn':
            return vn_grid_props.loadProps(temp)

        else:
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
    
    @classmethod
    def loadProps(cls, dct):
        inputs = ['mas', 'fieldname', 'space', 'color', 'species', 'gal_res', 'color_cut']
        prm = []
        for i in inputs:
            try:
                val = dct.pop(i)
            except KeyError:
                val = None
            
            prm.append(val)
        
        return galaxy_grid_props(prm[0], prm[1], prm[2], prm[3], prm[4], prm[5], prm[6])

    def isCompatible(self, other):
        op = other.props
        sp = self.props

        # for galaxyXgalaxy
        if op['fieldname'] == sp['fieldname']:
            stmass_or_total = op['species'] == sp['species']
            resdef_match = op['gal_res'] == sp['gal_res'] and op['gal_res'] == 'diemer'
            coldef_match = op['color_cut'] == sp['color_cut'] and sp['color_cut'] == '0.60'
            return stmass_or_total and resdef_match and coldef_match and super().isCompatible(other)
        
        # hiptlXgalaxy handled by hiptl
        
        # hisubhaloXgalaxy handled by hisubhalo

        # vnXgalaxy handled by vn

        # galaxyXptl handled by ptl
        return super().isCompatible(other)

    def isIncluded(self):

        def test(cds, mts, schts):
            cdtest = self.props['color_cut'] in cds
            mtest = self.props['species'] in mts
            mastest = self.props['mas'] in schts
            return cdtest and mtest and mastest
        
        def only_pk():
            self.props['compute_xi'] = False
            self.props['compute_slice'] = False

        # if self.props['gal_res'] == 'papastergis_SDSS':
        #     cds = ['papastergis_SDSS']
        #     ms = ['stmass']
        #     schts = ['CIC']
        #     only_pk()
        #     return test(cds, ms, schts)
        
        # elif self.props['gal_res'] == 'wolz_wiggleZ':
        #     cds = ['wolz_wiggleZ']
        #     ms = ['stmass']
        #     schts = ['CIC']
        #     only_pk()
        #     return test(cds, ms, schts) and self.props['color'] == 'red'
        
        # elif self.props['gal_res'] == 'wolz_eBOSS_ELG':
        #     cds = ['wolz_eBOSS_ELG']
        #     ms = ['stmass']
        #     schts = ['CIC']
        #     only_pk()
        #     return test(cds, ms, schts) and self.props['color'] == 'blue'

        # elif self.props['gal_res'] == 'wolz_eBOSS_LRG':
        #     cds = ['wolz_eBOSS_LRG']
        #     ms = ['stmass']
        #     schts = ['CIC']
        #     only_pk()
        #     return test(cds, ms, schts) and self.props['color'] == 'red'

        # elif self.props['gal_res'] == 'anderson_2df':
        #     cds = ['anderson_2df']
        #     ms = ['stmass']
        #     schts = ['CIC']
        #     only_pk()
        #     return test(cds, ms, schts)


        # everything that isn't a color definition associated with an observation is fine
        if self.props['gal_res'] == 'diemer':
            obs_color_cuts = rl.galaxyObsColorDefs()
            coldef_is_compatible = not (self.props['color_cut'] in obs_color_cuts)
            # CIC between stmass and all mass should be the same - removing redundancy
            is_CICW = self.props['mas'] == 'CICW'
            is_CIC_and_stmass = self.props['mas'] == 'CIC' and self.props['species'] == 'stmass'

            return coldef_is_compatible and (is_CICW or is_CIC_and_stmass)

        elif 'threshold' in self.props['gal_res'] or 'bin' in self.props['gal_res']:
            fid_colcut = self.props['color_cut'] == '0.60'
            only_pk()
            is_cicw = self.props['mas'] == 'CICW'
            is_stmass = self.props['species'] == 'stmass'
            return fid_colcut and is_cicw and is_stmass
        # # if this is gridprop obj for resolved, then
        # elif self.props['color'] == 'resolved':
        #     # removing redundancy in CIC with both kinds of mass
        #     is_CICW = self.props['mas'] == 'CICW'
        #     is_CIC_and_stmass = self.props['mas'] == 'CIC' and self.props['species'] == 'stmass'
        #     return is_CICW or is_CIC_and_stmass
        
        elif self.props['color'] == 'all':
            is_CICW = self.props['mas'] == 'CICW'
            is_CIC_and_stmass = self.props['mas'] == 'CIC' and self.props['species'] == 'stmass'
            return is_CICW or is_CIC_and_stmass
        return False

############################################################################################################

class hiptl_grid_props(grid_props):

    def __init__(self, mas, field, space, model, mass_or_temp):
        other = {}
        other['map'] = mass_or_temp
        other['model'] = model
        super().__init__(mas, field, space, other)
        return
    
    @classmethod
    def loadProps(cls, dct):
        inputs = ['mas', 'fieldname', 'space', 'model', 'map']
        prm = []
        for i in inputs:
            try:
                val = dct.pop(i)
            except KeyError:
                val = None
            
            prm.append(val)
        
        return hiptl_grid_props(prm[0], prm[1], prm[2], prm[3], prm[4])
    
    def isCompatible(self, other):
        sp = self.props
        op = other.props

        # hiptl/h2ptlXgalaxy/galaxy_dust
        if 'galaxy' in op['fieldname']:
            # for comparisons to Anderson and Wolz -> stmass/resdef is eBOSS, wiggleZ, 2df
            if 'temp' == sp['map']:
                obs_defs = rl.galaxyObsColorDefs()
                obs_defs.remove('papastergis_SDSS')
                match_obs = op['gal_res'] in obs_defs and op['color_cut'] in obs_defs
                return match_obs and super().isCompatible(other)
            
            # if a mass map, it is either diemer
            elif op['gal_res'] == 'diemer':
                # the important color definitions
                # cols = ['0.60', '0.55', '0.65', 'visual_inspection']

                # also include resolved
                is_resolved = op['color'] == 'resolved'

                return (op['color_cut'] == '0.60' or is_resolved) and super().isCompatible(other)
            
            # ignore all papa resdefs -> hisubhalo is more comparable
            elif op['gal_res'] == 'papastergis_SDSS':
                return False
            
            # if all = color, then include
            elif op['color'] == 'all':
                return True

        # hiptlXptl
        else:
            # include if mass map, not temp map
            return sp['map'] == 'mass' and super().isCompatible(other)

############################################################################################################

class hisubhalo_grid_props(grid_props):

    def __init__(self, mas, field, space, model, HI_res):
        other = {}
        other['model'] = model
        splt = model.split('_')
        other['projection'] = splt[-1]
        other['HI_res'] = HI_res
        super().__init__(mas, field, space, other)
    
    @classmethod
    def loadProps(cls, dct):
        inputs = ['mas', 'fieldname', 'space', 'model', 'HI_res']
        prm = []
        for i in inputs:
            try:
                val = dct.pop(i)
            except KeyError:
                val = None
            
            prm.append(val)
        
        return hisubhalo_grid_props(prm[0], prm[1], prm[2], prm[3], prm[4])
    
    def isIncluded(self):
        def test(schts):
            mastest = self.props['mas'] in schts
            return mastest
        
        def only_pk():
            self.props['compute_xi'] = False
            self.props['compute_slice'] = False
            return
        
        
        sp = self.props
        if sp['HI_res'] == 'papastergis_ALFALFA':
            mas = ['CIC']
            only_pk()
            return test(mas) and sp['fieldname'] == 'hisubhalo'
        elif 'bin' in sp['HI_res'] or 'threshold' in sp['HI_res']:
            is_cicw = sp['mas'] == 'CICW'
            only_pk()
            return is_cicw

        return True
    
    def setupGrids(self, outfile):
        return super().setupGrids(outfile)
    
    def isCompatible(self, other):
        sp = self.props
        op = other.props
        # hisubhaloXgalaxy
        if 'galaxy' in op['fieldname']:
            # if both have papastergis resolution definition, include only hisubhalo
            if op['gal_res'] == 'papastergis_SDSS':
                #return sp['HI_res'] == 'papastergis_ALFALFA'
                return False # returning false because trying to compare to papastergis is
                # going to be qualitatively difficult
            
            # if diemer resdef, include certain color definitions and resolved definition
            elif op['gal_res'] == 'diemer':
                # cdefs = ['0.55','0.60','0.65', 'visual_inspection']
                is_resolved = op['color'] == 'resolved'
                return (op['color_cut'] in ['0.60'] or is_resolved) and super().isCompatible(other)
            
            # don't include other observational stuff temporarily
            elif op['gal_res'] == 'wolz_eBOSS_ELG':
                return False
            
            elif op['gal_res'] == 'wolz_eBOSS_LRG':
                return False
            
            elif op['gal_res'] == 'wolz_wiggleZ':
                return False
            
            elif op['gal_res'] == 'anderson_2df':
                return False
                
            # if all galaxies, also include
            elif op['color'] == 'all':
                return super().isCompatible(other)
            
            return False
        
        # elif op['fieldname'] == 'ptl':
        #     if sp['fieldname'] == 'hisubhalo':
        #         models = rl.getMolFracModelsGalHI()
        #     elif sp['fieldname'] == 'h2subhalo':
        #         models = rl.getMolFracModelsGalH2()
            
        #     return sp['model'] == models[0] # compute cross power with just one
        return super().isCompatible(other)

#############################################################################################################

class ptl_grid_props(grid_props):
    
    def __init__(self, mas, field, space, species):
        other = {'species':species}
        super().__init__(mas, field, space, other)
        return
    
    @classmethod
    def loadProps(cls, dct):
        inputs = ['mas', 'fieldname', 'space', 'species']
        prm = []
        for i in inputs:
            try:
                val = dct.pop(i)
            except KeyError:
                val = None
            
            prm.append(val)
        
        return ptl_grid_props(prm[0], prm[1], prm[2], prm[3])

    def isCompatible(self, other):
        op = other.props
        if op['fieldname'] == 'galaxy':
            fid_colcut = op['color_cut'] == '0.60'
            fid_res = op['gal_res'] == 'diemer'
            stsp = op['species'] == 'stmass'
            match = fid_colcut and fid_res and stsp
            return match and super().isCompatible(other)
        else:
            return super().isCompatible(other)
################################################################################################################

class vn_grid_props(grid_props):
    def __init__(self, mas, field, space, mass_or_temp):
        other = {}
        other['map'] = mass_or_temp

        super().__init__(mas, field, space, other)

    @classmethod
    def loadProps(cls, dct):
        inputs = ['mas', 'fieldname', 'space', 'map']
        prm = []
        for i in inputs:
            try:
                val = dct.pop(i)
            except KeyError:
                val = None
            
            prm.append(val)
        
        return vn_grid_props(prm[0], prm[1], prm[2], prm[3])
    
    def isCompatible(self, other):
        sp = self.props
        op = other.props

        # vnXgalaxy 
        if 'galaxy' in op['fieldname']:
            # for comparisons to Anderson and Wolz -> stmass/resdef is eBOSS, wiggleZ, 2df
            if 'temp' == sp['map']:
                obs = rl.galaxyObsColorDefs()
                obs.remove('papastergis_SDSS')
                obs_match = op['gal_res'] in obs and op['color_cut'] in obs
                return obs_match and super().isCompatible(other)
            
            # if a mass map, it is either diemer or papa
            elif op['gal_res'] == 'diemer':
                # the important color definitions
                # cols = ['0.60', '0.55', '0.65', 'visual_inspection']

                # also include resolved
                is_resolved = op['color'] == 'resolved'

                return (op['color_cut'] == '0.60' or is_resolved) and super().isCompatible(other)
            
            # ignore all papa resdefs -> hisubhalo is more comparable
            elif op['gal_res'] == 'papastergis_SDSS':
                return False
            
            # if all = base, then include
            elif op['color'] == 'all':
                return super().isCompatible(other)

        # vnXptl
        else:
            return sp['map'] == 'mass' and super().isCompatible(other)