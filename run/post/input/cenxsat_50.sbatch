#!/bin/bash
#SBATCH --requeue
#SBATCH --job-name=cenxsat_post
#SBATCH --output=/home/cosinga/scratch/hcolor/run/post/input/cenxsat_post.log
#SBATCH --ntasks=1
#SBATCH --mail-user=cosinga@umd.edu
#SBATCH --mail-type=ALL
#SBATCH --account=diemer-prj-astr
#SBATCH --mem-per-cpu=45805
#SBATCH --time=1-1:00:00

source ~/my-venv/bin/activate
python ~/scratch/hcolor/run/post/post_pk.py censat_tng100B_050S_0A_800R/grids/galaxygrid_tng100B_050S_0A_800R.hdf5 censat_tng100B_050S_0A_800R/grids/galaxygrid_tng100B_050S_0A_800R.hdf5 galxgal.txt ~/scratch/hcolor/run/post/results/cenxsat_50.hdf5
