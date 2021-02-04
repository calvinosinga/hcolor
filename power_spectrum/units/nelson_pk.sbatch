#!/bin/bash
#SBATCH --share
#SBATCH --job-name=nelson_pk
#SBATCH --time=6:00:00
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=150000
#SBATCH --account=astronomy-hi
#SBATCH --mail-type=ALL
#SBATCH --output=nelson_pk.dat
#SBATCH --mail-user=cosinga@umd.edu

. ~/.profile
python3 /lustre/cosinga/hcolor/power_spectrum/pk.py 'nelson_99.final.hdf5' 'nelson_99_pk' 
python3 /lustre/cosinga/hcolor/power_spectrum/pk.py 'nelson_high_99.final.hdf5' 'nelson_high_99_pk' 
python3 /lustre/cosinga/hcolor/power_spectrum/pk.py 'nelson_low_99.final.hdf5' 'nelson_low_99_pk' 
