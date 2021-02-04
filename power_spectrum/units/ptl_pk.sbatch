#!/bin/bash

#SBATCH --share
#SBATCH --job-name=ptl_pk
#SBATCH --time=4:00:00
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=150000
#SBATCH --account=astronomy-hi
#SBATCH --mail-type=ALL
#SBATCH --output=ptl_pk.dat
#SBATCH --mail-user=cosinga@umd.edu

. ~/.profile
python3 /lustre/cosinga/hcolor/power_spectrum/pk.py 'ptl_99.final.hdf5' 'ptl_99_pk' 
