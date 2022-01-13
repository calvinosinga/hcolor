"""
Takes user input
"""

class Input():
    ptl_runs = ['hiptl', 'h2ptl', 'hiptl_nH', 'ptl', 'vn']
    gcat_runs = ['galaxy', 'galaxy_dust', 'hisubhalo', 'h2subhalo']
    implemented = ptl_runs + gcat_runs
    simlist = ['tng100', 'tng100-3', 'tng100-2', 'tng50', 'tng300']
    snaplist = [99]
    axislist = [0,1,2]
    hydrogen_runs = ['hiptl', 'h2ptl', 'hiptl_nH', 'vn', 'hisubhalo', 'h2subhalo']
    matter_runs = ['galaxy', 'galaxy_dust', 'ptl']
    atomic_runs = ['hiptl', 'hisubhalo', 'vn', 'hiptl_nH']
    molecular_runs = ['h2subhalo', 'h2ptl']

    def __init__(self):
        self.rparams = self.getUserRunParams()
        self.runs = self.getFields()
        return

    def getUserRunParams(self):
        def _getParam(inmessage, comlist, errmessage, to_type = str):
            compatible = False
            while not compatible:
                val = input(inmessage)
                try:
                    val = to_type(val)
                except ValueError:
                    print("given value is not convertible to correct data type\n")
                else:
                    compatible = val in comlist
                    if not compatible:
                        print(errmessage+'\n')
            return val
        
        rp = {}
        rp['verbose'] = _getParam("verbosity (0,1):", [0,1], 'must be 0 or 1', int)

        rp['prefix'] = input("prefix for output names:")

        outstr = ''
        for s in self.simlist:
            outstr += s + ', '
        outstr = outstr[:-2]
        rp['sim'] = _getParam("simulation name (%s):"%outstr, self.simlist,
                "simulation name not in compatible list")
        
        rp['snap'] = _getParam("snapshot:", self.snaplist, 
                "snapshot not in compatible list: %s"%self.snaplist, int)
        
        rp['axis'] = _getParam("axis:", self.axislist,
                "axis not in compatible list", int)

        compatible = False
        while not compatible:
            res = input("grid resolution:")
            try:
                res = int(res)
            except ValueError:
                print("resolution given is not an integer \n")
            else:
                compatible = True
        rp['res'] = res        
        return rp

    def getFields(self):
        done = False
        runs = []
        while not done:
            field = input("fieldname (type done to exit): ")
            if not field in self.implemented:
                done = field == 'done'
                if not done:
                    print("not in implemented fields %s \n"%self.implemented)
            else:
                runs.append(field)
        return runs
    
    @classmethod
    def isPtl(cls, name):
        return name in cls.ptl_runs
    
    @classmethod
    def isCat(cls, name):
        return name in cls.gcat_runs
    
    @classmethod
    def isHyd(cls, name):
        return name in cls.hydrogen_runs
    
    @classmethod
    def isMat(cls, name):
        return name in cls.matter_runs
    
    @classmethod
    def isAtomic(cls, name):
        return name in cls.atomic_runs
    
    @classmethod
    def isMolecular(cls,name):
        return name in cls.molecular_runs
    
    def getParams(self):
        return self.rparams
    
    def getRuns(self):
        return self.runs
