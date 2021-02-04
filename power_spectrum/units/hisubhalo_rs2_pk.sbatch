#!/bin/bash

#SBATCH --share
#SBATCH --job-name=hisubhalo_rspk2
#SBATCH --time=1-10:00:00
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=150000
#SBATCH --account=astronomy-hi
#SBATCH --mail-type=ALL
#SBATCH --output=hisubhalo_rspk2.dat
#SBATCH --mail-user=cosinga@umd.edu

. ~/.profile
python3 /lustre/cosinga/hcolor/power_spectrum/rspk.py 'hisubhalo_rs_99.final.hdf5' 'hisubhalo_rs_99_pk' 2
