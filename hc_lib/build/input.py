"""
Takes user input
"""

class Input():
    ptl_runs = ['hiptl', 'h2ptl', 'hiptl_nH', 'ptl', 'vn']
    gcat_runs = ['galaxy', 'galaxy_dust', 'hisubhalo', 'h2subhalo']
    implemented = ptl_runs + gcat_runs
    simlist = ['tng100']
    snaplist = [99]
    axislist = [0,1,2]
    hydrogen_runs = ['hiptl', 'h2ptl', 'hiptl_nH', 'vn', 'hisubhalo', 'h2subhalo']
    matter_runs = ['galaxy', 'galaxy_dust', 'ptl']

    def __init__(self):
        self.rparams = self.getUserRunParams()
        self.runs = self.getFields()
        return

    def getUserRunParams(self):
        def _getParam(inmessage, comlist, errmessage, to_type = str):
            compatible = False
            while not compatible:
                val = input(inmessage+'\n')
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
        rp['verbose'] = _getParam("verbosity (0,1):", [0,1], 'must be 0 or 1\n', int)

        rp['prefix'] = input("prefix for output names:")

        outstr = ''
        for s in self.simlist:
            outstr += s + ', '
        outstr = outstr[:-2]
        rp['sim'] = _getParam("simulation name (%s)"%outstr, self.simlist,
                "simulation name not in compatible list")
        
        rp['snap'] = _getParam("snapshot :", self.snaplist, 
                "snapshot not in compatible list: %s"%self.snaplist, int)
        
        rp['axis'] = _getParam("axis: ", self.axislist,
                "axis not in compatible list", int)

        compatible = False
        while not compatible:
            res = input("grid resolution: ")
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
                print("not in implemented fields %s \n"%self.impmented)
            else:
                runs.append(field)
        return runs
        
    def isPtl(self, name):
        return name in self.ptl_runs
    
    def isCat(self, name):
        return name in self.gcat_runs
    def isHyd(self, name):
        return name in self.hydrogen_runs
    
    def isMat(self, name):
        return name in self.matter_runs
    def getParams(self):
        return self.rparams
    
    def getRuns(self):
        return self.runs