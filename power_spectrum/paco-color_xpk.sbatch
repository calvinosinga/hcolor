#!/bin/bash
#SBATCH --share
#SBATCH --job-name=paco-color_xpk
#SBATCH --time=10:00:00
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=250000
#SBATCH --account=astronomy-hi
#SBATCH --mail-type=ALL
#SBATCH --output=paco-color_xpk.dat
#SBATCH --mail-user=cosinga@umd.edu

. ~/.profile
python3 /lustre/cosinga/hcolor/power_spectrum/xpk.py 'paco_99.final.hdf5' 'ALL' 'nelson_mid_99.final.hdf5' 'ALL' 'paco-nelson_mid_99_xpk'
