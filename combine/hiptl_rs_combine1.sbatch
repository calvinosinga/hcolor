#!/bin/bash

#SBATCH --share
#SBATCH --job-name=hptlrs_combine1
#SBATCH --output=out_hiptl_combine1.dat
#SBATCH --time=2-1:00:00
#SBATCH --ntasks=1
#SBATCH --mail-user=cosinga@umd.edu
#SBATCH --account=astronomy-hi
#SBATCH --mem-per-cpu=80000
#SBATCH --mail-type=ALL

. ~/.profile
python3 /lustre/cosinga/hcolor/combine/hiptl_combine.py 100 200 99 "hiptl_rs_"

