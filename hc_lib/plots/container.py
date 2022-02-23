from hc_lib.build.input import Input
import numpy as np

class ResultContainer():
    def __init__(self, field_obj, result_type, grid_props, runtime, xvalues, yvalues = [], 
            zvalues = [], Nmodes = [], count = -1):
        self.xvalues = xvalues
        self.yvalues = yvalues
        self.zvalues = zvalues
        self.Nmodes = Nmodes
        self.rt = result_type
        self.count = count
        self.props = {}
        self.props['result_runtime'] = runtime
        self.props['is_auto'] = True
        self._extract_field_properties(field_obj)
        self._extract_grid_properties(grid_props)
        return
    
    def getType(self):
        return self.rt
    
    def _extract_field_properties(self, f):
        self.props['box'] = f.box
        self.props['simname'] = f.simname
        if '-2' in f.simname:
            self.props['sim_resolution'] = 'medium'
        elif '-3' in f.simname:
            self.props['sim_resolution'] = 'low'
        else:
            self.props['sim_resolution'] = 'high'
        self.props['num_part'] = f.numDMpart
        self.props['grid_resolution'] = f.grid_resolution
        self.props['snapshot'] = f.snapshot
        self.props['redshift'] = f.header['Redshift']
        self.props['axis'] = f.axis
        self.props['fieldname'] = f.fieldname
        self.props['is_hydrogen'] = Input.isHyd(f.fieldname)
        self.props['is_atomic'] = Input.isAtomic(f.fieldname)
        self.props['is_molecular'] = Input.isMolecular(f.fieldname)
        self.props['is_particle'] = Input.isPtl(f.fieldname)
        self.props['is_groupcat'] = Input.isCat(f.fieldname)
        self.props['is_matter'] = Input.isMat(f.fieldname)
        return
    
    def _extract_grid_properties(self, gp):
        self.props.update(gp.props)
        return

    def addCrossedField(self, other_rc):
        temp = {}
        oprop = other_rc.props
        skip = ['is_auto']
        for k,v in oprop.items():
            self_val = self.getProp(k)

            if not k in skip:
                if self_val is None:
                    temp[k] = [v]
                else:
                    temp[k] = [v, self_val]
        
        for k,v in self.props.items():
            if not k in temp:
                temp[k] = [v]

        self.props = temp
        self.props['is_auto'] = False
        return

    def getProp(self, prop_key):
        try:
            v = self.props[prop_key]
            if self.props['is_auto']:
                return v
            elif len(v) == 1:
                return v[0]
            else:
                return v
                
        except KeyError:
            return None
    
                
    def addProp(self, key, val):
        self.props[key] = val
        return
        
    def getValues(self):
        return self.xvalues, self.yvalues, self.zvalues

class PostResult(ResultContainer):

    def __init__(self):
        self.xvalues = []
        self.yvalues = []
        self.zvalues = []
        self.rt = ''
        self.props = {}
        return
    
    def computeBiasTheory(self, cross_rc, auto_rc):
        if not cross_rc.getType() == auto_rc.getType():
            raise ValueError('need to be same result type')
        self.rt = 'bias'

        # assuming that the result containers are power spectra

        # wavenum stay the same
        self.xvalues = cross_rc.xvalues
        self.yvalues = cross_rc.yvalues / auto_rc.yvalues

        # auto props should already be in the cross props
        self.props = cross_rc.props
        self.props['is_bias'] = True
        self.props['has_stoch'] = False
        return

    def computeBiasObs(self, numer, denom):
        if not numer.getType() == denom.getType():
            raise ValueError('need to be same result type')

        self.rt = 'bias'

        self.xvalues = numer.xvalues
        self.yvalues = np.sqrt(numer.yvalues / denom.yvalues)

        self.props = numer.props
        self.addCrossedField(denom.props)
        self.props['is_bias'] = True
        self.props['has_stoch'] = True
        return

    def computeRatio(self, numer, denom):
        if not numer.getType() == denom.getType():
            raise ValueError('need to be same result type')

        self.rt = 'ratio'

        self.xvalues = numer.xvalues
        self.yvalues = numer.yvalues / denom.yvalues

        self.props = numer.props
        self.addCrossedField(denom)
        self.props['is_ratio'] = True
        return
