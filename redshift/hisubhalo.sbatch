#!/bin/bash

#SBATCH --share
#SBATCH --job-name=hisubhalo_rs
#SBATCH --time=6:00:00
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=100000
#SBATCH --account=astronomy-hi
#SBATCH --mail-type=ALL
#SBATCH --mail-user=cosinga@umd.edu
#SBATCH --output=hisubhalo_rs.dat

. ~/.profile
python3 /lustre/cosinga/hcolor/redshift/hisubhalo.py 99
