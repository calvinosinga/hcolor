#!/bin/bash
#SBATCH --requeue
#SBATCH --job-name=cenxsat_post
#SBATCH --output=/home/cosinga/scratch/hcolor/run/cenxsat_post.log
#SBATCH --ntasks=1
#SBATCH --mail-user=cosinga@umd.edu
#SBATCH --mail-type=ALL
#SBATCH --account=diemer-prj-astr
#SBATCH --mem-per-cpu=45805
#SBATCH --time=1-1:00:00

hcsrc
python post_pk.py fiducial_tng100B_050S_0A_800R/grids/galaxygrid_tng100B_050S_0A_800R.hdf5 fiducial_tng100B_050S_0A_800R/grids/ptlcombine2_tng100B_050S_0A_800R.hdf5 galxptl.txt galxptl_50.hdf5
