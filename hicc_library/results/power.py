"""
Defines the Power class, which is where the information necessary to create a power spectrum
is stored.
"""
from hicc_library.results.result_super import Result
from Pk_library import Pk
import time
import numpy as np
import h5py as hp


class Power(Result):
    
    def __init__(self, gridfile, outfile, grids_for_results):
        super().__init__(gridfile, outfile)

        self.gridlist = grids_for_results

        return
    
    def compute(self):
        return
    
    def save_to_hdf5(self):
        return
    