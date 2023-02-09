import copy
from tabnanny import check
import hc_lib.fields.run_lib as rl

def check_gal_cut(ss, cut):
    if ss == 99:
        return cut == '0.60'
    elif ss == 67:
        return cut == '0.55'
    elif ss == 50:
        return cut == '0.50'

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
                gal_resolution_def, color_cut, censat):
        other = {}
        lst = [color, species, gal_resolution_def, color_cut, censat]
        keys = ['color', 'gal_species', 'gal_res','color_cut', 'censat']
        for i in range(len(lst)):
            other[keys[i]] = lst[i]

        super().__init__(mas, field, space, other)

        return
    
    @classmethod
    def loadProps(cls, dct):
        inputs = ['mas', 'fieldname', 'space', 'color', 'gal_species', 'gal_res', 'color_cut', 'censat']
        prm = []
        for i in inputs:
            try:
                val = dct.pop(i)
            except KeyError:
                val = None
            
            prm.append(val)
        
        return galaxy_grid_props(prm[0], prm[1], prm[2], prm[3], prm[4], prm[5], prm[6], prm[7])

    def isCompatible(self, other, snap):
        op = other.props
        sp = self.props

        # for galaxyXgalaxy
        if op['fieldname'] == sp['fieldname']:
            both_stmass = op['gal_species'] == 'stmass' and sp['gal_species'] == 'stmass'
            both_diemer = sp['gal_res'] == 'diemer' and op['gal_res'] == 'diemer'
            both_fid_cc = check_gal_cut(snap, sp['color_cut']) and check_gal_cut(snap, op['color_cut'])
            not_same = (not op['color'] == sp['color']) and (not op['censat'] == sp['censat'])
            both_none = sp['color_cut'] == 'None' and op['color_cut'] == 'None'
            return both_stmass and both_diemer and (both_fid_cc or both_none) and not_same and super().isCompatible(other)
        
        # hiptlXgalaxy handled by hiptl
        
        # hisubhaloXgalaxy handled by hisubhalo

        # vnXgalaxy handled by vn

        # galaxyXptl handled by ptl
        return super().isCompatible(other)

    def isIncluded(self):
        
        def only_pk():
            self.props['compute_xi'] = False
            self.props['compute_slice'] = False


        if self.props['gal_res'] == 'diemer':
            obs_color_cuts = rl.galaxyObsColorDefs()
            coldef_is_compatible = not (self.props['color_cut'] in obs_color_cuts)
            # CIC between stmass and all mass should be the same - removing redundancy
            is_CICW = self.props['mas'] == 'CICW'
            # is_CIC_and_stmass = self.props['mas'] == 'CIC' and self.props['species'] == 'stmass'

            return coldef_is_compatible and is_CICW

        elif 'threshold' in self.props['gal_res'] or 'bin' in self.props['gal_res']:
            fid_colcut = self.props['color_cut'] == '0.60'
            is_resolved = self.props['color'] == 'resolved'
            only_pk()
            is_stmass = self.props['gal_species'] == 'stmass'
            return (fid_colcut or is_resolved) and is_stmass
        
        # if there isnt' a resolution definition, must be 'all'
        elif self.props['color'] == 'all':
            is_CICW = self.props['mas'] == 'CICW'
            is_stmass = self.props['gal_species'] == 'stmass'
            return is_CICW and is_stmass

        return False

############################################################################################################

class hiptl_grid_props(grid_props):

    def __init__(self, mas, field, space, model, mass_or_temp):
        other = {}
        other['map'] = mass_or_temp
        other['model'] = model
        other['HI_fieldname'] = field
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
    
    def isIncluded(self):
        sp = self.props
        if not sp['model'] == 'GD14':
            self.props['compute_xi'] = False
            self.props['compute_slice'] = False
        return super().isIncluded and self.props['map'] == 'mass'
    
    def isCompatible(self, other, snap):
        sp = self.props
        op = other.props

        # hiptl/h2ptlXgalaxy
        if 'galaxy' in op['fieldname']:
            
            # if a mass map, it is either diemer
            if op['gal_res'] == 'diemer':
                # the important color definitions
                # cols = ['0.60', '0.55', '0.65', 'visual_inspection']

                # also include resolved
                is_resolved = op['color'] == 'resolved'
                fid_colcut = check_gal_cut(snap, op['color_cut'])
                is_stmass = op['gal_species'] == 'stmass'
                galcheck = (is_resolved or fid_colcut) and is_stmass

                
                return galcheck and super().isCompatible(other)
            
            elif 'bin' in op['gal_res'] or 'threshold' in op['gal_res']:
                # is_resolved = op['color'] == 'resolved'
                # fid_colcut = op['color_cut'] == '0.60'
                # is_stmass = op['species'] == 'stmass'
                # galcheck = (is_resolved or fid_colcut) and is_stmass

                
                # return galcheck and super().isCompatible(other)
                return False # Just want to compare with hisubhalo

            
            # if all = color, then exclude
            elif op['color'] == 'all':
                return False

        # hiptlXptl
        else:
            # include if mass map, not temp map
            return sp['map'] == 'mass' and super().isCompatible(other)

############################################################################################################

class hisubhalo_grid_props(grid_props):

    def __init__(self, mas, field, space, model, HI_res, censat):
        other = {}
        other['model'] = model
        splt = model.split('_')
        other['projection'] = splt[-1]
        other['HI_res'] = HI_res
        other['HI_fieldname'] = field
        other['censat'] = censat
        super().__init__(mas, field, space, other)
    
    @classmethod
    def loadProps(cls, dct):
        inputs = ['mas', 'fieldname', 'space', 'model', 'HI_res', 'censat']
        prm = []
        for i in inputs:
            try:
                val = dct.pop(i)
            except KeyError:
                val = None
            
            prm.append(val)
        
        return hisubhalo_grid_props(prm[0], prm[1], prm[2], prm[3], prm[4], prm[5])
    
    def isIncluded(self):
        
        def only_pk():
            self.props['compute_xi'] = False
            self.props['compute_slice'] = False
            return
        
        sp = self.props
        if 'bin' in sp['HI_res'] or 'threshold' in sp['HI_res']:
            # calculate auto power spectrum to test how clustering changes
            # with HI mass

            only_pk()
            return sp['mas'] == 'CICW'
        else:
            return sp['mas'] == 'CICW'
    
    def setupGrids(self, outfile):
        return super().setupGrids(outfile)
    
    def isCompatible(self, other, snap):
        sp = self.props
        op = other.props


        # hisubhaloXgalaxy
        if 'galaxy' in op['fieldname']:
            # we have diemer, bin/threshold gal_res to handle

            # if diemer resdef, include fiducial color_cut and resolved definition
            if op['gal_res'] == 'diemer':
                is_resolved = op['color'] == 'resolved'
                fid_colcut = check_gal_cut(snap, op['color_cut'])
                is_stmass = op['gal_species'] == 'stmass'
                # don't want total mass
                check_gal_props = (is_resolved or fid_colcut) and is_stmass

                # also make sure they are in the same space and have same MAS
                return check_gal_props and super().isCompatible(other)
            

            elif 'bin' in op['gal_res'] or 'threshold' in op['gal_res']:
                is_resolved = op['color'] == 'resolved'
                fid_colcut = check_gal_cut(snap, op['color_cut'])
                is_stmass = op['gal_species'] == 'stmass'
                check_gal_props = (is_resolved or fid_colcut) and is_stmass

                # only calculate cross-power with fiducial HI_res
                is_diemer = sp['HI_res'] == 'diemer'

                return check_gal_props and is_diemer and super().isCompatible(other)

            
            elif op['color'] == 'all':
                return False
            
            return False
        # hisubhaloXgalaxy_dust
        
        # hisubhaloXhisubhalo
        elif 'hisubhalo' == op['fieldname']:
            model_match = op['model'] == sp['model']
            return model_match and super().isCompatible(other)
        # hisubhaloXptl - default setting
        return super().isCompatible(other)

#############################################################################################################

class ptl_grid_props(grid_props):
    
    def __init__(self, mas, field, space, species):
        other = {'ptl_species':species}
        super().__init__(mas, field, space, other)
        return
    
    @classmethod
    def loadProps(cls, dct):
        inputs = ['mas', 'fieldname', 'space', 'ptl_species']
        prm = []
        for i in inputs:
            try:
                val = dct.pop(i)
            except KeyError:
                val = None
            
            prm.append(val)
        
        return ptl_grid_props(prm[0], prm[1], prm[2], prm[3])

    def isCompatible(self, other, snap):
        op = other.props
        if op['fieldname'] == 'galaxy':
            fid_colcut = check_gal_cut(snap, op['color_cut'])
            is_resolved = op['color'] == 'resolved'
            fid_res = op['gal_res'] == 'diemer'
            stsp = op['gal_species'] == 'stmass'
            match = (fid_colcut or is_resolved) and fid_res and stsp
            return match and super().isCompatible(other)
        elif op['fieldname'] == 'galaxy_dust':
            return False
        else:
            return super().isCompatible(other)
################################################################################################################

class vn_grid_props(grid_props):
    def __init__(self, mas, field, space, mass_or_temp):
        other = {}
        other['map'] = mass_or_temp
        other['HI_fieldname'] = field
        super().__init__(mas, field, space, other)
        return

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
    
    def isCompatible(self, other, snap):
        sp = self.props
        op = other.props

        # vnXgalaxy 
        if 'galaxy' in op['fieldname']:
            
            if op['gal_res'] == 'diemer':
                # the important color definitions
                # cols = ['0.60', '0.55', '0.65', 'visual_inspection']

                # also include resolved
                is_resolved = op['color'] == 'resolved'
                fid_colcut = check_gal_cut(snap, op['color_cut'])
                is_stmass = op['gal_species'] == 'stmass'
                check_gal = (is_resolved or fid_colcut) and is_stmass


                return check_gal and super().isCompatible(other)
            
            elif 'bin' in op['gal_res'] or 'threshold' in op['gal_res']:
                return False
            
            # if all = base, then exclude
            elif op['color'] == 'all':
                return False

        # vnXptl
        else:
            return sp['map'] == 'mass' and super().isCompatible(other)
