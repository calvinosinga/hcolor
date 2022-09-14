
#!/bin/bash
#SBATCH --requeue
#SBATCH --job-name=post_process
#SBATCH --output=/home/cosinga/scratch/hcolor/fig_md_analysis/post_process.log
#SBATCH --ntasks=1
#SBATCH --mail-user=cosinga@umd.edu
#SBATCH --mail-type=ALL
#SBATCH --account=diemer-prj-aac
#SBATCH --time=10:00:00
#SBATCH --mem-per-cpu=10000

hcsrc
python3 /home/cosinga/scratch/hcolor/fig_md_analysis/post_process.py