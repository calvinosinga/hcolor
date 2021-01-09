#!/bin/bash

#SBATCH --share
#SBATCH --job-name=paco_pk
#SBATCH --time=4:00:00
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=150000
#SBATCH --account=astronomy-hi
#SBATCH --mail-type=ALL
#SBATCH --output=paco_pk.dat
#SBATCH --mail-user=cosinga@umd.edu

. ~/.profile
python3 /lustre/cosinga/hcolor/power_spectrum/pk.py 'paco_HI_99.final.hdf5' 'paco_HI_99_pk'
python3 /lustre/cosinga/hcolor/power_spectrum/pk.py 'paco_m_99.final.hdf5' 'paco_m_99_pk'
