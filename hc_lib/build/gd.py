"""
Class for creating and interfacing with the global dictionary (gd) that is used to store io paths to needed files
on various computers.
"""
import os
class IODict():

    def __init__(self, run_params, runs, out_path, tng_path, hcolor_path):
        self.global_dict = {}
        self.path_dict = {}
        self.rparams = run_params
        self.addSimPaths(tng_path)
        self.addOutPaths(out_path, runs)
        self.addPyPaths(hcolor_path)
        # other odds and ends to add to gd
        self.global_dict['pickles'] = {}
        self.global_dict['verbose'] = run_params['verbose']
        return
    
    def addSimPaths(self, tng_path):
        gd = self.global_dict
        simname = self.rparams['sim']
        snap = self.rparams['snap']

        gd[simname] = tng_path
        gd['snapshot'] = gd[simname]+'snapdir_%03d/snap_%03d.'%(snap,snap) + "%d.hdf5"
        # the last %d is the chunk, given during run stage
        gd['load_header'] = gd['snapshot']%(0)
        gd['TREECOOL'] = gd[simname]+'TREECOOL_fg_dec11'
        # add postprocessing paths
        post = gd[simname] + 'postprocessing/'
        gd['dust'] = post + 'stellar_light/'+ \
                'Subhalo_StellarPhot_p07c_cf00dust_res_conv_ns1_rad30pkpc_%03d.hdf5'%snap
        gd['hih2catsh'] = post +'/hih2/hih2_galaxy_%03d.hdf5'%snap
        gd['hih2ptl'] = post + '/hih2/hih2_particles_%03d'%snap + ".%d.hdf5"
        # the chunk is given during the run stage
        return
    
    def addOutPaths(self, out_path, runs):
        rp = self.rparams
        pd = self.path_dict
        rtup = (rp['prefix'], rp['sim'], rp['snap'], rp['axis'], rp['res'])
        outdir = out_path+'%s_%sB_%03dS_%dA_%dR/'%rtup

        if not os.path.isdir(outdir):
            os.mkdir(outdir)
        pd['output'] = outdir
        
        def create_subdirectory(subdir, savepath = True):
            os.mkdir(outdir+subdir+'/')
            splt = subdir.split("/")
            # make sure they aren't saving over other paths
            if savepath:
                pd[splt[-1]] = outdir + subdir+'/'
            
            return

        create_subdirectory("grids")
        create_subdirectory("sbatch")
        create_subdirectory("sbatch/logs")
        create_subdirectory("results")
        create_subdirectory("results/plots")

        for i in runs:
            create_subdirectory("results/plots/"+i, False)
            create_subdirectory("sbatch/logs/"+i, False)
        return

    def getGlobalDict(self):
        return self.global_dict
    
    def getPathDict(self):
        return self.path_dict

    def add(self, key, val):
        self.global_dict[key] = val
        return
    
    def addPyPaths(self, hcolor_path):
        pd = self.path_dict
        pd['auto_result'] = hcolor_path+'run/auto.py'
        pd['cross_result'] = hcolor_path+'run/cross.py'
        pd['create_grid'] = hcolor_path + 'run/create_grid.py'
        pd['combine'] = hcolor_path + 'run/combine.py'
        return
