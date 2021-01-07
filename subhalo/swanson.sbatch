#!/bin/bash

#SBATCH --share
#SBATCH --job-name=swanson
#SBATCH --time=2:00:00
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=100000
#SBATCH --account=astronomy-hi
#SBATCH --mail-type=ALL
#SBATCH --mail-user=cosinga@umd.edu
#SBATCH --output=swanson.dat

. ~/.profile
python3 /lustre/cosinga/hcolor/hisubhalo/swanson.py 448 99
