import os
import pickle as pkl
import numpy as np
from collections.abc import Iterable

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
                    rowLabels.append(str(rowlab))
                
                if not collab in colLabels:
                    colLabels.append(str(collab))
                
        rowLabels.sort()
        colLabels.sort()

        nrows = len(rowLabels)
        ncols = len(colLabels)

        # saves an array of lists of result containers, each element corresponds
        # to a panel in the final figure
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

    def getVals(self, result_type, propname, include_props = None):
        """
        Returns all of the unique instances of that property within
        the ResultLibrary
        """
        results = self._getResultType(result_type)
        vals = []
        for r in results:
            try:
                if r.props[propname] not in vals:
                    if include_props is None:
                        vals.append(r.props[propname])
                    elif r.matchProps(include_props):
                        vals.append(r.props[propname])
            except KeyError:
                continue

        
        return vals
    
    def printLib(self, include_props, result_type = ''):
        print('######## RESULT LIBRARY #################\n')
        rts = ['pk', '2Dpk', 'xi', 'slice']
        rtitle = ['1D power spectra', '2D power spectra',
                '1D correlation', 'slices']
        rdict = {rts[i]:rtitle[i] for i in range(len(rts))}

        if result_type == '':
            for r in rdict:
                rnames= []
                print('list of result names for %s:'%rdict[r])

                res_list = self._getResultType(r)

                for result in res_list:
                    fn = result.props['fieldname']
                    sn = result.props['simname']
                    ss = result.props['snapshot']
                    ax = result.props['axis']
                    greso = result.props['grid_resolution']
                    rstr = '%s_%sB_%03dS_%dA_%dR'%(fn,sn,ss,ax,greso)
                    rnames.append(rstr)
                print(rnames)

                print()
        
        else:

            res_list = self._getResultType(result_type)

            print('list of result names for %s:'%rdict[result_type])
            

            for result in res_list:
                if result.matchProps(include_props):
                    print(result.props)
            
            print()
        return
