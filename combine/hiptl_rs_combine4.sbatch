#!/bin/bash

#SBATCH --share
#SBATCH --job-name=hptlrs_combine4
#SBATCH --output=out_hiptlrs_combine4.dat
#SBATCH --time=2-22:00:00
#SBATCH --ntasks=1
#SBATCH --mail-user=cosinga@umd.edu
#SBATCH --account=astronomy-hi
#SBATCH --mem-per-cpu=80000
#SBATCH --mail-type=ALL

. ~/.profile
python3 /lustre/cosinga/hcolor/combine/hiptl_combine.py 400 448 99 "hiptl_rs_"

