import os
import pickle as pkl
import numpy as np

class ResultLibrary():

    def __init__(self):
        self.slices = []
        self.pks = []
        self.xis = []
        self.tdpks = []
        self.hists = []
        return
    

    def getPaths(self, directory):
        paths = []
        for (root, dirs, files) in os.walk(directory):
            for fl in files:
                filepath = os.path.join(root, fl)
                if ".pkl" in filepath and not "gd.pkl" in filepath and not ".hdf5" in filepath:
                    paths.append(filepath)
        
        return paths
        

    def addResults(self, directory = '', pkl_file = ''):
        if not directory == '':
            paths = self.getPaths(directory)
            for p in paths:
                obj = pkl.load(open(p, 'rb'))
                if not obj.getSlices() is None:
                    self.slices.extend(obj.getSlices())
                self.pks.extend(obj.getPks())
                self.xis.extend(obj.getXis())
                self.tdpks.extend(obj.get2Dpks())
                #if 'galaxy' == obj.fieldname:
                    #self.hists.extend(obj.hists)

        elif not pkl_file == '':
            obj = pkl.load(open(pkl_file, 'rb'))
            self.slices.extend(obj.getSlices())
            self.pks.extend(obj.getPks())
            self.xis.extend(obj.getXis())
            self.tdpks.extend(obj.get2Dpks())
        
        return

    def _getResultType(self, result_type):
        if result_type == 'pk':
            result = self.pks
        elif result_type == '2Dpk':
            result = self.tdpks
        elif result_type == 'xi':
            result = self.xis
        elif result_type == 'slice':
            result = self.slices
        else:
            raise ValueError('unsupported result type given')
        return result
        

    def organizeFigure(self, includep, rowp, colp, result_type):
        """
        includep is dict that stores a property and the value that it should have.
        rowp is the property that separates each row
        colp is the property that separates each column
        """
        rowLabels = []
        colLabels = []
        forFig = []
        
        result = self._getResultType(result_type)

        for r in result:
            if r.matchProps(includep):
                forFig.append(r)
                rowlab = r.getProp(rowp)
                collab = r.getProp(colp)

                if not rowlab in rowLabels:
                    rowLabels.append(rowlab)
                
                if not collab in colLabels:
                    colLabels.append(collab)
                
        rowLabels.sort()
        colLabels.sort()
        nrows = len(rowLabels)
        ncols = len(colLabels)
        figArr = np.empty((nrows, ncols), dtype=object)
        for i in range(nrows):
            for j in range(ncols):
                temp = []
                for f in range(len(forFig)):
                    rowres = forFig[f].getProp(rowp)
                    colres = forFig[f].getProp(colp)
                    if rowres == rowLabels[i] and colres == colLabels[j]:
                        temp.append(forFig[f])
                figArr[i, j] = temp
        return figArr, rowLabels, colLabels

    def getVals(self, result_type, propname):
        """
        Returns all of the unique instances of that property within
        the ResultLibrary
        """
        results = self._getResultType(result_type)
        vals = []
        for r in results:
            if r.props[propname] not in vals:
                vals.append(r.props[propname])
        
        return vals
