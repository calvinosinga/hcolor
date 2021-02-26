#!/bin/bash

#SBATCH --share
#SBATCH --job-name=hiptl_rs_final
#SBATCH --output=out_hiptl_rs_final.dat
#SBATCH --time=1-1:00:00
#SBATCH --ntasks=1
#SBATCH --mail-user=cosinga@umd.edu
#SBATCH --account=astronomy-hi
#SBATCH --mem-per-cpu=80000
#SBATCH --mail-type=ALL

. ~/.profile
python3 /lustre/cosinga/hcolor/combine/final_hiptl.py 'hiptl_rs_' 99

