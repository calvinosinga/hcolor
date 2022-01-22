import os
import pickle as pkl
import numpy as np
import copy

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
        
    def getResult(self, iprops, result_type):
        results = self._getResultType(result_type)
        one_prop = []
        for r in results:
            if self.matchProps(r, iprops):
                one_prop.append(r)
        
        if len(one_prop) > 1:
            print('more than one result retrieved: %d results'%len(one_prop))
            for i in one_prop:
                print(i.props)
        return one_prop[0]
        
    def addResults(self, runname, directory = '', pkl_file = ''):
        if not directory == '':
            paths = self.getPaths(directory)
            for p in paths:
                obj = pkl.load(open(p, 'rb'))
                self._addRunnameProp(obj, runname)
                # if not obj.getSlices() is None:
                #     self.slices.extend(obj.getSlices())
                # self.pks.extend(obj.getPks())
                # self.xis.extend(obj.getXis())
                # self.tdpks.extend(obj.get2Dpks())
                # if obj.fieldname == 'galaxy' or obj.fieldname == 'galaxy_dust':
                #     self.hists.extend(obj.hists)

        elif not pkl_file == '':
            obj = pkl.load(open(pkl_file, 'rb'))
            self.slices.extend(obj.getSlices())
            self.pks.extend(obj.getPks())
            self.xis.extend(obj.getXis())
            self.tdpks.extend(obj.get2Dpks())
        
        return

    def _addRunnameProp(self, obj, runname):
        def _addRunnameLoop(results, self_results):
            for r in results:
                r.addProp('runname', runname)
            self_results.extend(results)
            return
        
        pks = obj.getPks()
        _addRunnameLoop(pks, self.pks)
        xis = obj.getXis()
        _addRunnameLoop(xis, self.xis)
        slices = obj.getSlices()
        if not slices is None:
            _addRunnameLoop(slices, self.slices)

        tdpks = obj.get2Dpks()
        _addRunnameLoop(tdpks, self.tdpks)
        if obj.fieldname == 'galaxy' or obj.fieldname == 'galaxy_dust':
            hists = obj.hists
            _addRunnameLoop(hists, self.hists)
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
        elif result_type == 'hist':
            result = self.hists
        else:
            raise ValueError('unsupported result type given')
        return result
    
    def getProp(self, rc, key):
        try:
            return rc.props[key]
        except KeyError:
            return 'no key'

    def matchProps(self, rc, desired_props, verbose=False):
        isMatch = True
        for k,v in desired_props.items():
            self_val = self.getProp(rc, k)
            
            if self_val == 'no key':
                continue

            # if we don't have a list of desired values, check if the property
            # of the result has the the desired value. Auto powers only have one
            # property to check
            elif not isinstance(v, list) and not isinstance(self_val, list):
                isMatch = (isMatch and v == self_val)
            # if we do have a list of desired values, but the result is still an
            # auto power spectrum, check if self_val is in v
            elif isinstance(v, list) and not isinstance(self_val, list):
                isMatch = (isMatch and self_val in v)

            # if both are lists, we need to know if at least one value from self_val
            # is in the desired properties
            elif isinstance(v, list) and isinstance(self_val, list):
                one_val = False
                for i in range(len(self_val)):
                    if self_val[i] in v:
                        one_val = True
                isMatch = (isMatch and one_val)
            # the last case where v is not a list but self_val is
            elif not isinstance(v, list) and isinstance(self_val, list):
                isMatch = (isMatch and v in self_val)
            else:
                print('not all cases handled')
        return isMatch

    def organizeFigure(self, includep, rowp, colp, result_type, removep = {}, check = None,
                default_labels = True, rowlabels = [], collabels = []):
        """
        includep is dict that stores a property and the value that it should have.
        rowp is the property that separates each row
        colp is the property that separates each column
        """
        if not rowlabels:
            has_row_order = True
        if not collabels:
            has_col_order = True
        rowLabels = []
        colLabels = []
        forFig = []
        result = self._getResultType(result_type)
        for r in result:
           
            if self.matchProps(r, includep, True):
                forFig.append(r)
                rowlab = self.getProp(r, rowp)
                collab = self.getProp(r, colp)
                
                if not rowlab in rowLabels:
                    rowLabels.append(rowlab)
                
                if not collab in colLabels:
                    colLabels.append(collab)

        if not has_row_order:      
            rowLabels.sort()
        if not has_col_order:
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
                    rowres = self.getProp(forFig[f],rowp)
                    colres = self.getProp(forFig[f],colp)
                    if rowres == rowLabels[i] and colres == colLabels[j]:
                        temp.append(forFig[f])
                figArr[i, j] = temp
        
        if not check is None:
            self._checkPanel(figArr[check[0], check[1]], includep, rowp, colp)
        
        if default_labels:
            rowLabels =  self._defaultLabels(rowp, rowLabels)
            colLabels = self._defaultLabels(colp, colLabels)
        return figArr, rowLabels, colLabels

    def _defaultLabels(self, prop, labels):
        if prop == 'redshift':
            newl = []
            for i in labels:
                if isinstance(i, list):
                    newl.append(r'z=%.1f'%round(i[0]))
                else:
                    newl.append(r'z=%.1f'%round(i))
            return newl
        elif prop == 'space':
            newl = []
            for i in labels:
                if isinstance(i, list):
                    newl.append(i[0].capitalize() + ' Space')
                else:
                    newl.append(i.capitalize() + ' Space')
            return newl
        elif prop == 'color':
            def _make_color_label(name):
                l = name
                if name == 'all':
                    l = 'All Subhalos'
                elif name == 'resolved':
                    l = 'All Galaxies'
                else:
                    l = name.capitalize() + ' Galaxies'
                return l
            
            newl = []
            for i in labels:
                if isinstance(i, list):
                    c1 = _make_color_label(i[0])
                    c2 = _make_color_label(i[1])
                    if not c1 == c2:
                        
                        newl.append('%s - %s'%(c1,c2))
                    else:
                        newl.append(c1)
                else:
                    newl.append(_make_color_label(i))
            return newl
        elif prop == 'axis':
            
            if isinstance(labels[0], list):
                return ['Axis=%d'%i[0] for i in labels]
            else:
                return [r'Axis=%d'%i for i in labels]
        elif prop == 'box':
            if isinstance(labels[0], list):
                return ['%d$^3$ (Mpc/h)$^3$'%round(i[0]) for i in labels]
            else:
                return ['%d$^3$ (Mpc/h)$^3$'%round(i) for i in labels]
        elif prop == 'sim_resolution':
            if isinstance(labels[0], list):
                return [i[0].capitalize() + ' Resolution' for i in labels]
            else:
                return [i.capitalize() + ' Resolution' for i in labels]
        elif prop == 'grid_resolution':
            if isinstance(labels[0], list):
                return ['%d$^3$ Bins'%i[0] for i in labels]
            else:
                return ['%d$^3$ Bins'%i for i in labels]
        else:
            return labels
            
    def _checkPanel(self, results, includep, rowp, colp):
        
        vals = {}
        for rc in results:
            rprops = rc.props
            for k,v in rprops.items():
                not_include = not k in includep
                not_row_col = not (k == rowp or k == colp)
                if not_include and not_row_col:
                    if not k in vals:
                        vals[k] = [v]
                    elif v not in vals[k]:
                        vals[k].append(v)
                
        for v in vals:
            if len(vals[v]) > 1:
                print('more than one value for prop %s'%v)
                print(vals[v])
                print()
                    
        return

    def removeResults(self, figArr, remove_dict):
        dim = figArr.shape
        for i in range(dim[0]):
            for j in range(dim[1]):
                rpanel = figArr[i, j]
                for r in rpanel:
                    if self.matchProps(r, remove_dict):
                        rpanel.remove(r)
                figArr[i, j] = rpanel

        return figArr
    
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
                    elif self.matchProps(r,include_props):
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
                if self.matchProps(result, include_props):
                    print(result.props)
            
            print()
        return
