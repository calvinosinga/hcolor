#!/bin/bash
#SBATCH --share
#SBATCH --job-name=hiptl-all_xpk
#SBATCH --time=15:00:00
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=150000
#SBATCH --account=astronomy-hi
#SBATCH --mail-type=ALL
#SBATCH --output=hiptl-all_xpk.dat
#SBATCH --mail-user=cosinga@umd.edu

. ~/.profile
python3 /lustre/cosinga/hcolor/power_spectrum/xpk.py 'hiptl_99.final.hdf5' 'ALL' 'swanson_99.final.hdf5' 'ALL' 'hiptl-swanson_99_xpk'
python3 /lustre/cosinga/hcolor/power_spectrum/xpk.py 'hiptl_99.final.hdf5' 'ALL' 'nelson_99.final.hdf5' 'blue' 'hiptl-nelson_99_xpk'
python3 /lustre/cosinga/hcolor/power_spectrum/xpk.py 'hiptl_99.final.hdf5' 'ALL' 'nelson_99.final.hdf5' 'red' 'hiptl-nelson_99_xpk'
python3 /lustre/cosinga/hcolor/power_spectrum/xpk.py 'hiptl_99.final.hdf5' 'ALL' 'nelson_99.final.hdf5' 'nondetection' 'hiptl-nelson_99_xpk'
python3 /lustre/cosinga/hcolor/power_spectrum/xpk.py 'hiptl_99.final.hdf5' 'ALL' 'nelson_99.final.hdf5' 'detection' 'hiptl-nelson_99_xpk'
python3 /lustre/cosinga/hcolor/power_spectrum/xpk.py 'hiptl_99.final.hdf5' 'ALL' 'ptl_99.final.hdf5' 'ALL' 'hiptl-ptl_99_xpk'
