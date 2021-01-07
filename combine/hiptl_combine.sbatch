#!/bin/bash

#SBATCH --share
#SBATCH --job-name=hiptl_combine
#SBATCH --output=out_hiptl_combine.dat
#SBATCH --time=12:00:00
#SBATCH --ntasks=1
#SBATCH --mail-user=cosinga@umd.edu
#SBATCH --account=astronomy-hi
#SBATCH --mem-per-cpu=80000
#SBATCH --mail-type=ALL

. ~/.profile
python3 /lustre/cosinga/hcolor/combine/hiptl_combine.py 0 10 99
