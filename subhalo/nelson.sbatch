#!/bin/bash

#SBATCH --share
#SBATCH --job-name=nelson
#SBATCH --time=8:00:00
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=100000
#SBATCH --account=astronomy-hi
#SBATCH --mail-type=ALL
#SBATCH --mail-user=cosinga@umd.edu
#SBATCH --output=nelson.dat

. ~/.profile
python3 /lustre/cosinga/hcolor/subhalo/nelson.py 448 99 'mid' 'CIC'
python3 /lustre/cosinga/hcolor/subhalo/nelson.py 448 99 'high' 'CIC'
python3 /lustre/cosinga/hcolor/subhalo/nelson.py 448 99 'low' 'CIC'
