"""
Class for creating and interfacing with the global dictionary (gd) that is used to store io paths to needed files
on various computers.
"""
import os
import copy

class IODict():

    def __init__(self, run_params, runs, out_path, tng_path, hcolor_path):
        self.input_dict = {}
        self.path_dict = {}
        self.rparams = run_params
        self.runs = runs
        self.addSimPaths(tng_path)
        self.addOutPaths(out_path)
        self.addPyPaths(hcolor_path)
        # other odds and ends to add to gd
        self.input_dict['pickles'] = {}
        self.input_dict['verbose'] = run_params['verbose']
        self.input_dict['galaxy_runtype'] = run_params['galaxy_runtype']
        self.input_dict['hisubhalo_runtype'] = run_params['hisubhalo_runtype']
        return
    
    def addSimPaths(self, tng_path):
        idict = self.input_dict
        simname = self.rparams['sim']
        snap = self.rparams['snap']

        idict[simname] = tng_path
        idict['groupcat'] = tng_path + 'output/'
        idict['snapshot'] = idict[simname]+'output/snapdir_%03d/snap_%03d.'%(snap,snap) + "%d.hdf5"
        # the last %d is the chunk, given during run stage
        idict['load_header'] = idict['snapshot']%(0)
        if simname == 'tng300':
            simpath = '/lustre/cosinga/L205n2500TNG/'
            idict['TREECOOL'] = simpath +'TREECOOL_fg_dec11'
            post = simpath + 'postprocessing/'
            idict['hih2catsh'] = post +'hih2/hih2_galaxy_%03d.hdf5'%snap
            idict['hih2ptl'] = post + 'hih2/hih2_particles_%03d'%snap + ".%d.hdf5"
        # add postprocessing paths
        post = idict[simname] + 'postprocessing/'
        idict['dust'] = post + 'stellar_light/'+ \
                'Subhalo_StellarPhot_p07c_cf00dust_res_conv_ns1_rad30pkpc_%03d.hdf5'%snap

        # the chunk is given during the run stage
        return
    
    def addOutPaths(self, out_path):
        rp = self.rparams
        pd = self.path_dict
        rtup = (rp['prefix'], rp['sim'], rp['snap'], rp['axis'], rp['res'])
        outdir = out_path+'%s_%sB_%03dS_%dA_%dR/'%rtup

        if not os.path.isdir(outdir):
            os.mkdir(outdir)
        pd['output'] = outdir
        
        def create_subdirectory(subdir, savepath = 0):
            os.mkdir(outdir+subdir+'/')
            splt = subdir.split("/")
            # make sure they aren't saving over other paths
            if savepath == 0:
                pd[splt[-1]] = outdir + subdir+'/'
            elif savepath == 1:
                pd[splt[-1]+'_'+splt[-2]] = outdir + subdir + '/'

            return

        create_subdirectory("grids")
        create_subdirectory("sbatch")
        create_subdirectory("sbatch/logs")
        create_subdirectory("results")

        for i in self.runs:
            create_subdirectory("sbatch/logs/"+i, 2)
        return

    def getGlobalDict(self):
        gd = copy.copy(self.input_dict)
        gd['grids'] = self.path_dict['grids']
        return gd
    
    def getInputDict(self):
        return self.input_dict

    def getPathDict(self):
        return self.path_dict

    def add(self, key, val):
        self.input_dict[key] = val
        return
    
    def addPyPaths(self, hcolor_path):
        pd = self.path_dict
        pd['auto_result'] = hcolor_path+'run/auto.py'
        pd['cross_result'] = hcolor_path+'run/cross.py'
        pd['create_grid'] = hcolor_path + 'run/create_grid.py'
        pd['combine'] = hcolor_path + 'run/combine.py'
        return
    
