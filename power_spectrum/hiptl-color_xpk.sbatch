#!/bin/bash
#SBATCH --share
#SBATCH --job-name=hiptl-nelson_xpk
#SBATCH --time=2-15:00:00
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=150000
#SBATCH --account=astronomy-hi
#SBATCH --mail-type=ALL
#SBATCH --output=hiptl-nelson_xpk.dat
#SBATCH --mail-user=cosinga@umd.edu

. ~/.profile
python3 /lustre/cosinga/hcolor/power_spectrum/xpk.py 'hiptl_99.final.hdf5' 'ALL' 'nelson_mid_99.final.hdf5' 'ALL' 'hiptl-nelson_mid_99_xpk'
