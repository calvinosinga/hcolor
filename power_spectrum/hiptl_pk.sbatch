#!/bin/bash

#SBATCH --share
#SBATCH --job-name=hiptl_pk
#SBATCH --time=4:00:00
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=150000
#SBATCH --account=astronomy-hi
#SBATCH --mail-type=ALL
#SBATCH --output=hiptl_pk.dat

. ~/.profile
python3 /lustre/cosinga/hcolor/power_spectrum/pk.py 
