#!/bin/bash

#SBATCH --share
#SBATCH --job-name=aggregate
#SBATCH --time=2:00:00
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=100000
#SBATCH --account=astronomy-hi
#SBATCH --mail-type=ALL
#SBATCH --mail-user=cosinga@umd.edu
#SBATCH --output=aggregate.dat

. ~/.profile
python3 /lustre/cosinga/hcolor/subhalo/aggregate_fields.py
