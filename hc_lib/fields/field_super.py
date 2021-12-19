"""
This file is responsible for the creation of the contituent sbatch files that make
up the pipeline.
"""
import illustris_python as il
import numpy as np
import h5py as hp
from Pk_library import Pk, Xi, XPk, XXi
import copy
import time
from hc_lib.build.input import Input

class grid_props():
    
    def __init__(self, mas, field, space, other_props,
                compute_xi = True, compute_slice = True):
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
        print("saveProps method has started...")
        for k,v in self.props.items():
            if not v is None:
                h5set.attrs[k] = v
        return
    
    @classmethod
    def loadProps(cls, dct):
        return grid_props(dct.pop('mas'), 
                dct.pop("fieldname"), dct.pop('space'), dct)
    
    def isCompatible(self, other):
        """
        Reports if two grids are compatible for cross-correlation
        """
        mas = self.props['mas'] == other.props['mas']
        space = self.props['space'] == other.props['space']
        return mas and space

class ResultContainer():
    def __init__(self, field_obj, grid_props, runtime, xvalues, yvalues = None, 
            zvalues = None, Nmodes = None):
        self.xvalues = xvalues
        self.yvalues = yvalues
        self.zvalues = zvalues
        self.Nmodes = Nmodes
        self.props = {}
        self.props['result_runtime'] = runtime
        self.props['is_auto'] = True
        self._extract_field_properties(field_obj)
        self._extract_grid_properties(grid_props)
        return
    
    
    def _extract_field_properties(self, f):
        self.props['box'] = f.box
        self.props['simname'] = f.simname
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
        for k,v in self.props.items():
            skip = ['is_auto']
            if not k in skip:
                othprop = other_rc.getProp(k)
                if v == othprop:
                    temp[k] = v
                else:
                    temp[k] = [v, othprop]
        self.props = temp
        self.props['is_auto'] = False
        return

    def getProp(self, prop_key):
        try:
            return self.props[prop_key]
        except KeyError:
            return None
    
    def matchProps(self, desired_props):
        isMatch = True
        for k,v in desired_props.items():
            self_val = self.getProp(k)

            if isinstance(v, list) and isinstance(self_val, list):
                matchone = v[0] == self_val[0] and v[1] == self_val[1]
                matchtwo = v[0] == self_val[1] and v[1] == self_val[0]
                isMatch = isMatch and (matchone or matchtwo)
            elif isinstance(self_val, list):
                isMatch = isMatch and v in self_val
            else:
                isMatch = isMatch and v == self_val


        return isMatch
    
    def addProp(self, key, val):
        self.props[key] = val
        return
        
    def getValues(self):
        return self.xvalues, self.yvalues, self.zvalues
        

    

class Field():

    def __init__(self, simname, snapshot, axis, resolution, pkl_path, verbose):
        # getting default class variables
        self.simname = simname
        self.snapshot = snapshot
        self.grid_resolution = resolution
        self.axis = axis
        self.pkl_path = pkl_path
        self.v = verbose
        
        self.pks = []
        self.xi = []
        self.slices = []
        self.tdpks = []

        if self.v:
            print("\n\ninputs given to superclass constructor:")
            print("the simulation name: %s"%self.simname)
            print("the snapshot: %d"%self.snapshot)
            print("the axis: %d"%self.axis)
            print("the grid resolution: %d"%self.grid_resolution)
            print("the pickle path: %s"%self.pkl_path)
        
        self.header = None # dictionary that stores basic sim info
        
        # other variables expected to be assigned values in subclasses
        self.gridprops = self.getGridProps()
        return
    
    def getGridProps(self):
        return {}
    
    
    def loadHeader(self, snappath):
        f = hp.File(snappath, 'r')
        self.header = dict(f['Header'].attrs)
        temp = dict(f['Parameters'].attrs)
        paramparams = ['BoxSize', 'HubbleParam']
        for p in paramparams:
            self.header[p] = temp[p]
        self.header['BoxSize'] *= self.header["Time"]/1e3
        # don't want to use self._convertPos(..) because that might change in subclasses
        self.header['MassTable'] *= 1e10/self.header['HubbleParam']
        self.box = self.header['BoxSize']
        self.numDMpart = self.header['NumPart_Total'][1]
        if self.v:
            print("finished loading header...")
            print(self.header)
        return
    
    def setupGrids(self, outfile):
        if self.v:
            print("starting to compute grids...")
        if self.header is None:
            raise ValueError("header needs to be loaded before computing grids")
        dat = outfile.create_dataset('pickle', data=[0])
        dat.attrs['path'] = self.pkl_path
        if self.v:
            print("the saved pickle path: %s"%self.pkl_path)
        return
    
    def computeGrids(self, outfile):
        pass


    def computePk(self, grid, grid_props):
        start = time.time()
        arr = grid.getGrid()
        arr = self._toOverdensity(arr)
        pk = Pk(arr, self.header["BoxSize"], axis = self.axis, MAS='CIC')
        runtime = time.time() - start

        rc = ResultContainer(self, grid_props, runtime, pk.k3D, pk.Pk[:,0], 
                Nmodes = pk.Nmodes3D)
        self.pks.append(rc)
        if grid_props['space'] == 'redshift':
            rc2D = ResultContainer(self, grid_props, runtime, pk.kpar, pk.kper,
                    pk.Pk2D[:], pk.Nmodes2D)
            self.tdpks.append(rc2D)
        
        return
    
    def computeXi(self, grid, grid_props):
        if grid_props['compute_xi']:
            start = time.time()
            arr = grid.getGrid()
            arr = self._toOverdensity(arr)
            xi = Xi(arr, self.header["BoxSize"], axis = self.axis, MAS='CIC')
            runtime = time.time() - start
            rc = ResultContainer(self, grid_props, runtime, xi.r3D, xi.xi[:,0])
            self.xi.append(rc)
        return

    def makeSlice(self, grid, grid_props, perc=0.1, mid=None, avg = False):
        if grid_props['compute_slice']:
            start = time.time()
            arr = grid.getGrid()
            if avg:
                arr = arr[::2,::2,::2] + arr[1::2, 1::2, 1::2]
            dim = arr.shape[0]
            slcidx = int(perc*dim) # the percentage of the volume that should be binned
            if mid is None:
                mid = int(dim/2)
            slc = np.log10(np.sum(arr[:, mid-slcidx:mid+slcidx, :], axis=(self.axis+1)%3))
            runtime = time.time()-start
            rc = ResultContainer(self, grid_props, runtime, slc)
            self.slices.append(rc)
        return
    
    def saveData(self, outfile, grid, gp):
        # saves grid. resolution, rss (combine info if chunk) -> attrs
        dat = grid.saveGrid(outfile)
        print('calling saveprops method...')
        gp.saveProps(dat)
        return dat
    
    def equals(self, other_field):
        fntest = self.fieldname == other_field.fieldname
        sstest = self.snapshot == other_field.snapshot
        axtest = self.axis == other_field.axis
        voltest = self.header['BoxSize'] == other_field.header['BoxSize']
        restest = self.grid_resolution == other_field.grid_resolution
        return fntest and sstest and axtest and voltest and restest
    
    def getPks(self):
        return self.pks
    
    def get2Dpks(self):
        return self.tdpks
    
    def getSlices(self):
        return self.slices
    
    def getXis(self):
        return self.xi

    def _loadSnapshotData(self):
        """
        The fields that use snapshot data vary in what they need too much,
        so the implementation is left to the subclasses. ptl, for example, needs
        data on all of the particles whereas hiptl just needs gas particles.
        Thus anything put here will necessarily be overwritten anyway in a subclass.
        """
        pass
    
    def _loadGalaxyData(self, simpath, fields):
        return il.groupcat.loadSubhalos(simpath, self.snapshot, fields=fields)
    
    def _toRedshiftSpace(self, pos, vel):
        boxsize = self.header["BoxSize"] # Mpc/h
        hubble = self.header["HubbleParam"]*100 # defined using big H
        redshift = self.header['Redshift']

        factor = (1+redshift)/hubble
        pos[:,self.axis] += vel[:,self.axis]*factor

        # handle periodic boundary conditions
        pos[:, self.axis] = np.where((pos[:,self.axis]>boxsize) | (pos[:,self.axis]<0), 
                (pos[:,self.axis]+boxsize)%boxsize, pos[:,self.axis])
        
        return pos

    def _convertMass(self, mass):
        """
        Converts mass units from 1e10 M_sun/h to M_sun
        """
        mass *= 1e10/self.header['HubbleParam']
        return mass
    
    def _convertPos(self, pos):
        """
        Converts position units from ckpc/h to Mpc/h
        """
        pos *= self.header["Time"]/1e3
        return pos
    
    def _convertVel(self, vel):
        """
        Multiplies velocities by scale factor^0.5
        """
        vel *= np.sqrt(self.header["Time"])
        return vel
    
    def _convertDensity(self, density):
        # assuming that the density is given in 10^10 sm/h / (ckpc/h)**3
        density *= (self.header['Time']/1e3)**3
        density *= 1e10/self.header["HubbleParam"]
        return density

    def _toOverdensity(self, arr):
        arr = arr/self.header['BoxSize']**3
        arr = arr/np.mean(arr).astype(np.float32)
        arr = arr - 1

        return arr

    
from hc_lib.grid.grid import Grid
class Cross():
    def __init__(self, field1, field2, gridfilepath1, gridfilepath2):
        # the fieldname for this cross-power
        
        self.fieldname = field1.fieldname + 'X' + field2.fieldname
        self.field1 = field1
        self.field2 = field2
        self.gfpath1 = gridfilepath1
        self.gfpath2 = gridfilepath2

        self.xpks = []
        self.xxis = []
        self.tdxpks = []


        self.v = field1.v
        self.box = self.field1.header['BoxSize']
        self.axis = self.field2.axis
        self.snapshot = self.field1.snapshot
        self.grid_resolution = self.field1.grid_resolution
        self.simname = self.field1.simname
        return
    
    def _loadHdf5(self):
        gf1 = hp.File(self.gfpath1, 'r')
        gf2 = hp.File(self.gfpath2, 'r')
        return gf1, gf2
    
    def equals(self, other_cross):
        f11test = self.field1.equals(other_cross.field1)
        f22test = self.field2.equals(other_cross.field2)
        f12test = self.field1.equals(other_cross.field2)
        f21test = self.field2.equals(other_cross.field1)
        return (f11test and f22test) or (f12test and f21test)
    
    def getPks(self):
        return self.xpks
    
    def get2Dpks(self):
        return self.tdxpks
    
    def getSlices(self):
        return None
    
    def getXis(self):
        return self.xxis
    
    def computeXpks(self):
        if self.v:
            print("starting process of computing xpks...")
        gf1, gf2 = self._loadHdf5()
        keylist1 = self._getKeys(gf1)
        keylist2 = self._getKeys(gf2)
        gprops1 = self.field1.gridprops
        gprops2 = self.field2.gridprops
        for k1 in keylist1:
            for k2 in keylist2:
                gp1 = gprops1[k1]
                gp2 = gprops2[k2]
                if gp1.isCompatible(gp2) and gp2.isCompatible(gp1):
                    grid1 = Grid.loadGrid(gf1[k1])
                    grid2 = Grid.loadGrid(gf2[k2])
                    
                    self._xpk(grid1, grid2, gp1, gp2)
        return
    
    def _xpk(self, grid1, grid2, gp1, gp2):
        start = time.time()
        arrs = (self._toOverdensity(grid1.getGrid()), 
                self._toOverdensity(grid2.getGrid()))
        xpk = XPk(arrs, self.box, self.axis, MAS=['CIC','CIC'])
        runtime = time.time() - start

        rc1 = ResultContainer(self.field1, gp1, runtime, xpk.k3D, 
                xpk.XPk[:,0,0], Nmodes = xpk.Nmodes3D)
        rc2 = ResultContainer(self.field2, gp2, runtime, xpk.k3D,
                xpk.XPk[:,0,0], Nmodes=xpk.Nmodes3D)
        rc1.addCrossedField(rc2)
        self.xpks.append(rc1)

        do_2D = gp1['space'] == 'redshift' and gp2['space'] == 'redshift'
        if do_2D:
            if not self.saved_xk2D:
                self.kper = xpk.kper
                self.kpar = xpk.kpar
                self.saved_xk2D = True
            if not self.saved_Nmodes2D:
                self.Nmodes2D= xpk.Nmodes2D
                self.saved_Nmodes2D = True
            rc1 = ResultContainer(self.field1, gp1, runtime, xpk.kpar, xpk.kper,
                    xpk.PkX2D[:,0], Nmodes= xpk.Nmodes2D)
            rc2 = ResultContainer(self.field2, gp2, runtime, xpk.kpar, xpk.kper, 
                    xpk.PkX2D[:,0], Nmodes=xpk.Nmodes2D)
            rc1.addCrossedField(rc2)
            self.tdxpks.append(rc1)

        return

    def _getKeys(self, gfile):
        klist = list(gfile.keys())
        klist.remove('pickle')
        temp = copy.copy(klist)
        for k in temp:
            if gfile[k].attrs['gridname'] == -1:
                klist.remove(k)
        return klist

    def computeXxis(self):

        gf1, gf2 = self._loadHdf5()
        keylist1 = self._getKeys(gf1)
        keylist2 = self._getKeys(gf2)
        gprops1 = self.field1.gridprops
        gprops2 = self.field2.gridprops
        for k1 in keylist1:
            for k2 in keylist2:
                gp1 = gprops1[k1]
                gp2 = gprops2[k2]
                is_compatible = gp1.isCompatible(gp1) and gp2.isCompatible(gp2)
                for_xi = gprops1['compute_xi'] and gprops2['compute_xi']
                if is_compatible and for_xi:
                    grid1 = Grid.loadGrid(gf1[k1])
                    grid2 = Grid.loadGrid(gf2[k2])
                    self._xxi(grid1, grid2, gp1, gp2)
        return
    
    def _xxi(self, grid1, grid2, gp1, gp2):
        start = time.time()
        arrs = (self._toOverdensity(grid1.getGrid()), 
                self._toOverdensity(grid2.getGrid()))
        xxi = XXi(arrs[0], arrs[1], self.box, MAS=['CIC','CIC'], axis=self.axis)
        runtime = time.time() - start
        if not self.saved_xr:
            self.r = xxi.r3D
            self.saved_xr = True
        
        rc1 = ResultContainer(self.field1, gp1, runtime, xxi.r3D, xxi.xi[:,0])
        rc2 = ResultContainer(self.field2, gp2, runtime, xxi.r3D, xxi.xi[:,0])
        rc1.addCrossedField(rc2)
        self.xxis.append(rc1)

        return
    
    def _toOverdensity(self, arr):
        arr = arr/self.box**3
        arr = arr/np.mean(arr).astype(np.float32)
        arr = arr - 1

        return arr
