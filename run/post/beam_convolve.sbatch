#!/bin/bash
#SBATCH --requeue
#SBATCH --output=/home/cosinga/scratch/hcolor/beam_convolve.log
#SBATCH --ntasks=1
#SBATCH --mail-user=cosinga@umd.edu
#SBATCH --mail-type=ALL
#SBATCH --account=diemer-prj-astr
#SBATCH --time=1-1:00:00
#SBATCH --mem-per-cpu=44620


python3 /home/cosinga/scratch/hcolor/run/post/beam_convolve.py
