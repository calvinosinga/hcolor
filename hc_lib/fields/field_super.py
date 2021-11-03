"""
This file is responsible for the creation of the contituent sbatch files that make
up the pipeline.
"""
import illustris_python as il
import numpy as np
import h5py as hp
import matplotlib.pyplot as plt
from Pk_library import Pk, Xi, XPk, XXi
import copy
from hc_lib.plots import plot_lib as plib

class grid_props():
    
    def __init__(self, base, mas, field, other_props):
        self.props = {}
        self.props['base'] = base
        self.props['mas'] = mas
        self.props['field'] = field
        self.props.update(other_props)
        return
    
    def getName(self):
        out = ''
        for k, v in self.props.items():
            if not v is None and not k == 'field':
                out += "%s_"%v
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
        return grid_props(dct.pop('base'), dct.pop('mas'), 
                dct.pop("field"), dct)
    
    def isCompatible(self, other):
        """
        Reports if two grids are compatible for cross-correlation
        """
        return self.props['mas'] == other.props['mas']

    
class Field():

    def __init__(self, simname, snapshot, axis, resolution, pkl_path, verbose):
        # getting default class variables
        self.simname = simname
        self.snapshot = snapshot
        self.resolution = resolution
        self.axis = axis
        self.pkl_path = pkl_path
        self.v = verbose

        # class variables for results
        self.saved_k = False
        self.saved_k2D = False
        self.saved_r = False
        self.saved_Nmodes1D = False
        self.saved_Nmodes2D = False

        self.pks = {}
        self.xi = {}
        self.slices = {}
        self.tdpks = {}

        if self.v:
            print("\n\ninputs given to superclass constructor:")
            print("the simulation name: %s"%self.simname)
            print("the snapshot: %d"%self.snapshot)
            print("the axis: %d"%self.axis)
            print("the resolution: %d"%self.resolution)
            print("the pickle path: %s"%self.pkl_path)
        
        self.header = None # dictionary that stores basic sim info
        


        # other variables expected to be assigned values in subclasses
        self.fieldname = ''
        self.gridprops = self.getGridProps()
        self.isHI = True
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
        if self.v:
            print("finished loading header...")
            print(self.header)
        return
    
    def computeGrids(self, outfile):
        if self.v:
            print("starting to compute grids...")
        if self.header is None:
            raise ValueError("header needs to be loaded before computing grids")
        dat = outfile.create_dataset('pickle', data=[0])
        dat.attrs['path'] = self.pkl_path
        if self.v:
            print("the saved pickle path: %s"%self.pkl_path)
        return
    
    def computeAux(self):
        """
        Compute auxiliary information/plots
        """
        return
    
    def computePk(self, grid):
        arr = grid.getGrid()
        arr = self._toOverdensity(arr)
        pk = Pk(arr, self.header["BoxSize"], axis = self.axis, MAS='CIC')
        if not self.saved_k:
            self.pks['k'] = pk.k3D
            self.saved_k = True
        if not self.saved_Nmodes1D:
            self.pks['Nmodes']=pk.Nmodes1D
            self.saved_Nmodes1D = True

        self.pks[grid.gridname] = pk.Pk[:,0]

        if grid.in_rss:
            if not self.saved_k2D:
                self.tdpks['kper'] = pk.kper
                self.tdpks['kpar'] = pk.kpar
            if not self.saved_Nmodes2D:
                self.tdpks['Nmodes'] = pk.Nmodes2D
                self.saved_Nmodes2D = True
            self.tdpks[grid.gridname] = pk.Pk[:,0]
        
        return
    
    def computeXi(self, grid):
        if not grid.ignore:
            arr = grid.getGrid()
            arr = self._toOverdensity(arr)
            xi = Xi(arr, self.header["BoxSize"], axis = self.axis, MAS='CIC')
            if not self.saved_r:
                self.xi["r"]=xi.r3D
                self.saved_r = True
            self.xi[grid.gridname] = xi.xi[:,0]
        return

    def makeSlice(self, grid, perc=0.1, mid=None):
        if not grid.ignore:
            # cmap.set_under('w')
            arr = grid.getGrid()
            dim = arr.shape[0]
            slcidx = int(perc*dim) # the percentage of the volume that should be binned
            if mid is None:
                mid = int(dim/2)
            slc = np.log10(np.sum(arr[:, mid-slcidx:mid+slcidx, :], axis=(self.axis+1)%3))
            self.slices[grid.gridname] = slc
        return
    
    def saveData(self, outfile, grid, gp):
        # saves grid. resolution, rss (combine info if chunk) -> attrs
        dat = grid.saveGrid(outfile)
        gp.saveProps(dat)
        return dat
    
    def plotPks(self, plotdir):
        box = self.header['BoxSize']
        for pk in self.pks:
            plib.plotpks(self.pks['k'], self.pks, box, self.axis, 
                    self.resolution, keylist=[pk])
            
            plt.savefig(plotdir+pk+'_1Dpk.png')
            plt.clf()
        
        for pk in self.tdpks:
            plib.plot2Dpk(self.tdpks['kpar'], self.tdpks['kper'], self.tdpks[pk])
            plt.savefig(plotdir+pk+'_2Dpk.png')
            plt.clf()
        return

    def plotXis(self, plotdir):
        box = self.header['BoxSize']
        for x in self.xi:
            plib.plotxis(self.xi['r'], self.xi, box, self.axis, 
                    self.resolution, keylist=[x])
            plt.savefig(plotdir+x+'_1Dxi.png')
            plt.clf()
        return

    def equals(self, other_field):
        fntest = self.fieldname == other_field.fieldname
        sstest = self.snapshot == other_field.snapshot
        axtest = self.axis == other_field.axis
        voltest = self.header['BoxSize'] == other_field.header['BoxSize']
        restest = self.resolution == other_field.resolution
        return fntest and sstest and axtest and voltest and restest
    
    def getGridsForX(self, other):
        xgrids = {}
        for g in self.gridnames:
            xgrids[g] = other.gridnames
        return xgrids
    
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

    def exportResults(self, outfile):
        def add(indict, idf):
            for k,v in indict.items():
                outfile.create_dataset(k+idf, data=v, 
                        compression="gzip", compression_opts=9)
                return
        
        add(self.pks, '_pk')
        add(self.xi, '_xi')
        add(self.tdpks, '_2Dpk')
        add(self.slices, '_slc')
        return
        
from hc_lib.grid.grid import Grid
class Cross():
    def __init__(self, field1, field2, gridfilepath1, gridfilepath2):
        # the fieldname for this cross-power
        
        self.fieldname = field1.fieldname + 'X' + field2.fieldname
        self.field1 = field1
        self.field2 = field2
        self.gfpath1 = gridfilepath1
        self.gfpath2 = gridfilepath2

        self.saved_xk = False
        self.saved_xr = False
        self.saved_xk2D = False
        self.saved_Nmodes1D = False
        self.saved_Nmodes2D = False
        self.xpks = {}
        self.xxis = {}
        self.tdxpks = {}

        self.v = field1.v
        self.box = self.field1.header['BoxSize']
        self.axis = self.field2.axis
        self.snapshot = self.field1.snapshot
        self.resolution = self.field1.resolution
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
                if k1[-2:] == 'rs':
                    k1 = k1[:-2]
                if k2[-2:] == 'rs':
                    k2 = k2[:-2]
                gp1 = gprops1[k1]
                gp2 = gprops2[k2]
                print(gp1)
                print(gp2)
                if gp1.isCompatible(gp2) and gp2.isCompatible(gp1):
                    grid1 = Grid.loadGrid(gf1[k1])
                    grid2 = Grid.loadGrid(gf2[k2])

                    self._xpk(grid1, grid2)
        return
    
    def _xpk(self, grid1, grid2):
        if not grid1.ignore and not grid2.ignore and grid1.in_rss == grid2.in_rss:

            kname = '%sX%s'%(grid1.gridname, grid2.gridname)
            if self.v:
                print("computing xpk for %s"%kname)
            arrs = (self._toOverdensity(grid1.getGrid()), 
                    self._toOverdensity(grid2.getGrid()))
            xpk = XPk(arrs, self.box, self.axis, MAS=['CIC','CIC'])
            if not self.saved_xk:
                self.addXpk('k',xpk.k3D)
                self.saved_xk = True
            if not self.saved_Nmodes1D:
                self.addXpk('Nmodes',xpk.Nmodes1D)
                self.saved_Nmodes1D = True
            self.addXpk(kname, xpk.XPk[:,0,0])

            if grid1.in_rss and grid2.in_rss:
                if not self.saved_xk2D:
                    self.add2DXpk('kper', xpk.kper)
                    self.add2DXpk('kpar', xpk.kpar)
                    self.saved_xk2D = True
                if not self.saved_Nmodes2D:
                    self.add2DXpk('Nmodes', xpk.Nmodes2D)
                    self.saved_Nmodes2D = True
                self.add2DXpk(kname, xpk.PkX2D[:,0])

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
        if self.v:
            print("starting process of computing x-corrs...")
        gf1, gf2 = self._loadHdf5()
        keylist1 = self._getKeys(gf1)
        keylist2 = self._getKeys(gf2)
        gprops1 = self.field1.gridprops
        gprops2 = self.field2.gridprops
        for k1 in keylist1:
            for k2 in keylist2:
                if k1[-2:] == 'rs':
                    k1 = k1[:-2]
                if k2[-2:] == 'rs':
                    k2 = k2[:-2]
                gp1 = gprops1[k1]
                gp2 = gprops2[k2]
                if gp1.isCompatible(gp1) and gp2.isCompatible(gp2):
                    grid1 = Grid.loadGrid(gf1[k1])
                    grid2 = Grid.loadGrid(gf2[k2])
                    self._xxi(grid1, grid2)
        if self.v:
            print("x-corrs finished computing, results look like:")
            print(self.xxis)
        return
    
    def _xxi(self, grid1, grid2):
        if not grid1.ignore and not grid2.ignore and grid1.in_rss == grid2.in_rss:
            kname = '%sX%s'%(grid1.gridname, grid2.gridname)

            if self.v:
                print("computing x-corr for %s"%kname)
            
            arrs = (self._toOverdensity(grid1.getGrid()), 
                    self._toOverdensity(grid2.getGrid()))
            xxi = XXi(arrs[0], arrs[1], self.box, MAS=['CIC','CIC'], axis=self.axis)
            if not self.saved_xr:
                self.addXxi('r',xxi.r3D)
                self.saved_xr = True
            self.addXxi(kname, xxi.xi[:,0])

        return

    def addXpk(self, name, array):
        self.xpks[name] = array
        return
    
    def add2DXpk(self, name, array):
        self.tdxpks[name] = array
        return
    
    def addXxi(self, name, array):
        self.xxis[name] = array
        return
    
    def _toOverdensity(self, arr):
        arr = arr/self.box**3
        arr = arr/np.mean(arr).astype(np.float32)
        arr = arr - 1

        return arr

    def exportResults(self, outfile):
        def add(indict, idf):
            for k,v in indict.items():
                outfile.create_dataset(k+idf, data=v, 
                        compression="gzip", compression_opts=9)
                return
        
        add(self.xpks, '_xpk')
        add(self.xxi, '_xxi')
        add(self.tdxpks, '_2Dxpk')
        return