#!/bin/bash
#SBATCH --share
#SBATCH --requeue
#SBATCH --job-name=hiptl_grid_create
#SBATCH --output=/lustre/cosinga/hcolor/run/hydrotools.log
#SBATCH --mail-user=cosinga@umd.edu
#SBATCH --mail-type=ALL
#SBATCH --account=astronomy-hi
#SBATCH --time 1-1:00:00
#SBATCH --mem=100000
#SBATCH -n=1

python3 /lustre/cosinga/hcolor/run/hydrotools.py