#!/bin/bash

#SBATCH --share
#SBATCH --job-name=nelson_high
#SBATCH --time=6:00:00
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=100000
#SBATCH --account=astronomy-hi
#SBATCH --mail-type=ALL
#SBATCH --mail-user=cosinga@umd.edu
#SBATCH --output=nelson_high.dat

. ~/.profile
python3 /lustre/cosinga/hcolor/subhalo/units/nelson.py 448 99 'high'
