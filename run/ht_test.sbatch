#!/bin/bash

#SBATCH --share
#SBATCH --job-name=ht_test
#SBATCH --time=10:00:00
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=60000
#SBATCH --account=astronomy
#SBATCH --mail-type=ALL
#SBATCH --mail-user=cosinga@umd.edu
#SBATCH --output=htgr.dat

. ~/.profile
python3 /lustre/cosinga/hcolor/run/ht_test.py