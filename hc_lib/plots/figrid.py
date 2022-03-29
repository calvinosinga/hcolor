from hc_lib.plots.container import PostResult
import site
FGPATH = '/homes/cosinga/figrid/'
site.addsitedir(FGPATH)
from figrid.data_list import DataList
from figrid.figrid import Figrid
class HCFig():

    def __init__(self):
        self.dl = DataList()
        self.fg = None
        return
    
    def loadRlib(self, rlib):
        self.dl.loadResults(rlib.results['pk'])
        return
    
    def createFG(self):
        self.fg = Figrid(self.dl)
        return
    
    def 
