#!/bin/bash
#SBATCH --share
#SBATCH --job-name=paco-all_xpk
#SBATCH --time=10:00:00
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=250000
#SBATCH --account=astronomy-hi
#SBATCH --mail-type=ALL
#SBATCH --output=paco-all_xpk.dat
#SBATCH --mail-user=cosinga@umd.edu

. ~/.profile
python3 /lustre/cosinga/hcolor/power_spectrum/xpk.py 'paco_99.final.hdf5' 'ALL' 'swanson_99.final.hdf5' 'ALL' 'paco-swanson_99_xpk'
python3 /lustre/cosinga/hcolor/power_spectrum/xpk.py 'paco_99.final.hdf5' 'ALL' 'nelson_99.final.hdf5' 'ALL' 'paco-nelson_99_xpk'
python3 /lustre/cosinga/hcolor/power_spectrum/xpk.py 'paco_99.final.hdf5' 'ALL' 'nelson_low_99.final.hdf5' 'ALL' 'paco-nelson_low_99_xpk'
python3 /lustre/cosinga/hcolor/power_spectrum/xpk.py 'paco_99.final.hdf5' 'ALL' 'nelson_high_99.final.hdf5' 'ALL' 'paco-nelson_high_99_xpk'
