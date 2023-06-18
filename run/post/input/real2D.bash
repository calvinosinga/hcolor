#!/bin/bash
#SBATCH --requeue
#SBATCH --job-name=real2D
#SBATCH --output=/home/cosinga/scratch/hcolor/run/real2D.log
#SBATCH --ntasks=1
#SBATCH --mail-user=cosinga@umd.edu
#SBATCH --mail-type=ALL
#SBATCH --account=diemer-prj-astr
#SBATCH --mem-per-cpu=45805
#SBATCH --time=1-1:00:00

hcsrc
python post_pk.py fiducial_tng100B_099S_0A_800R/grids/vncombine2_tng100B_099S_0A_800R.hdf5 fiducial_tng100B_099S_0A_800R/grids/vncombine2_tng100B_099S_0A_800R.hdf5 vn_real2D.txt vnreal2D_99.hdf5
python post_pk.py fiducial_tng100B_099S_0A_800R/grids/galaxygrid_tng100B_099S_0A_800R.hdf5 fiducial_tng100B_099S_0A_800R/grids/galaxygrid_tng100B_099S_0A_800R.hdf5 real2D.txt real2D_99.hdf5
