"""
Super Class for results. Basically defines functions that all results use
that load in grid hdf5 files and interfaces with the file.
"""
import h5py as hp


class Result():
    def __init__(self, gridfile, outfile):
        self.gridfile = hp.File(gridfile, 'r')
        self.outfile = hp.File(outfile, 'w')
        return
        
        
    def getAttrs(self, gridname):
        return dict(self.gridfile[gridname])
    
    def makePlot(self):
        return
    
    def getData(self, gridname):
        return self.gridfile[gridname]
    
    def saveResult(self):
        
        pass

    def compute(self):
        pass
    
