#!/bin/bash

#SBATCH --share
#SBATCH --job-name=nelson-nelson_xpk
#SBATCH --time=1-10:00:00
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=250000
#SBATCH --account=astronomy-hi
#SBATCH --mail-type=ALL
#SBATCH --output=nelson-nelson_xpk.dat
#SBATCH --mail-user=cosinga@umd.edu

. ~/.profile
python3 /lustre/cosinga/hcolor/power_spectrum/xpk.py 'nelson_mid_99.final.hdf5' 'ALL' 'nelson_mid_99.final.hdf5' 'ALL' 'nelson_mid_99_xpk'
python3 /lustre/cosinga/hcolor/power_spectrum/xpk.py 'nelson_low_99.final.hdf5' 'ALL' 'nelson_low_99.final.hdf5' 'ALL' 'nelson_low_99_xpk'
python3 /lustre/cosinga/hcolor/power_spectrum/xpk.py 'nelson_high_99.final.hdf5' 'ALL' 'nelson_high_99.final.hdf5' 'ALL' 'nelson_high_99_xpk'
