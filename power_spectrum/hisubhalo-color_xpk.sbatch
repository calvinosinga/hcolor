#!/bin/bash
#SBATCH --share
#SBATCH --job-name=hisubhalo-color_xpk
#SBATCH --time=2-10:00:00
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=250000
#SBATCH --account=astronomy-hi
#SBATCH --mail-type=ALL
#SBATCH --output=hisubhalo-color_xpk.dat
#SBATCH --mail-user=cosinga@umd.edu

. ~/.profile
python3 /lustre/cosinga/hcolor/power_spectrum/xpk.py 'hisubhalo_99.final.hdf5' 'ALL' 'nelson_mid_99.final.hdf5' 'ALL' 'hisubhalo-nelson_mid_99_xpk'
python3 /lustre/cosinga/hcolor/power_spectrum/xpk.py 'hisubhalo_99.final.hdf5' 'ALL' 'nelson_low_99.final.hdf5' 'ALL' 'hisubhalo-nelson_low_99_xpk'
python3 /lustre/cosinga/hcolor/power_spectrum/xpk.py 'hisubhalo_99.final.hdf5' 'ALL' 'nelson_high_99.final.hdf5' 'ALL' 'hisubhalo-nelson_high_99_xpk'
