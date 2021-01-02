#!/bin/bash

#SBATCH --share
#SBATCH --job-name=hiptl_combine
#SBATCH --output=out_hiptl_combine.dat
#SBATCH --time=1:00:00
#SBATCH --ntasks=1
#SBATCH --mail-user=cosinga@umd.edu
#SBATCH --account=astronomy-hi
#SBATCH --mem-per-cpu=150000
#SBATCH --mail-type=ALL

cd /lustre/cosinga/hiptl_output
unzip -q -o 'hiptl_99.[0..1].hdf5.zip'
python3 /lustre/cosinga/hcolor/combine/hiptl_combine.py 0 1 99 no
