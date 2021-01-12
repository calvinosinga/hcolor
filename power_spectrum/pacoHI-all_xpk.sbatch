#!/bin/bash
#SBATCH --share
#SBATCH --job-name=paco-all_xpk
#SBATCH --time=4:00:00
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=150000
#SBATCH --account=astronomy-hi
#SBATCH --mail-type=ALL
#SBATCH --output=paco-all_xpk.dat
#SBATCH --mail-user=cosinga@umd.edu

. ~/.profile
python3 /lustre/cosinga/hcolor/power_spectrum/xpk.py 'paco_HI_99.final.hdf5' 'ALL' 'swanson_99.final.hdf5' 'ALL' 'pacoHI-swanson_99_xpk'
python3 /lustre/cosinga/hcolor/power_spectrum/xpk.py 'paco_HI_99.final.hdf5' 'ALL' 'nelson_99.final.hdf5' 'blue' 'pacoHI-nelson_99_xpk'
python3 /lustre/cosinga/hcolor/power_spectrum/xpk.py 'paco_HI_99.final.hdf5' 'ALL' 'nelson_99.final.hdf5' 'red' 'pacoHI-nelson_99_xpk'
python3 /lustre/cosinga/hcolor/power_spectrum/xpk.py 'paco_HI_99.final.hdf5' 'ALL' 'nelson_99.final.hdf5' 'nondetection' 'pacoHI-nelson_99_xpk'
python3 /lustre/cosinga/hcolor/power_spectrum/xpk.py 'paco_HI_99.final.hdf5' 'ALL' 'nelson_99.final.hdf5' 'detection' 'pacoHI-nelson_99_xpk'
python3 /lustre/cosinga/hcolor/power_spectrum/xpk.py 'paco_HI_99.final.hdf5' 'ALL' 'ptl_99.final.hdf5' 'ALL' 'pacoHI-ptl_99_xpk'
