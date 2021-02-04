#!/bin/python3

#SBATCH --share
#SBATCH --job-name=hiptl
#SBATCH --output=output_hiptl.dat
#SBATCH --time=2-8:00:00
#SBATCH --ntasks=50
#SBATCH --mail-user=cosinga@umd.edu
#SBATCH --mail-type=ALL
#SBATCH --account=astronomy-hi
#SBATCH --mem-per-cpu=60000

########################################################################################################
# 
# Job Distributor
#
# (c) Benedikt Diemer (diemer@umd.edu)
#
# This script serves as a batch file for the SLURM queuing system. It executes the commands stored in 
# each line of a file called commands.txt, each on a separate process (CPU). The purpose is to fill all 
# available processes as much as possible. The script outputs logs when new commands are started or 
# jobs end.
#
# Pro tip: try to list the commands that take the longest first. Otherwise, a time-intensive command
# might be started right at the end, leaving most CPUs without jobs.
#
########################################################################################################

import subprocess
import time
import os

########################################################################################################

def printLine():
    print('--------------------------------------------------------------')
    return

########################################################################################################
printLine()
print("Welcome to the job distributor.")
printLine()

start_time = time.time()

# N_PROC = int(float(os.environ["SLURM_JOB_CPUS_PER_NODE"]))
N_PROC = int(os.environ["SLURM_NTASKS"])
# Find commands to execute
f = open('/lustre/cosinga/hcolor/hiptl/units/commands_hiptl.txt', 'r')
#print(N_PROC)
commands = []
for line in f.readlines():
    commands.append(line.rstrip())
n_commands = len(commands)
print("Found " + str(n_commands) + " commands:")
for i in range(n_commands):
    print(i, commands[i])

printLine()

pipes = {}
i = 0
complete = 0

while complete < n_commands:
    
    keys = list(pipes.keys())
    for p in keys:
        if pipes[p].poll() is not None:
            complete += 1
            del pipes[p]

            dt = time.time() - start_time
            print("[%4d s] Completed  %3d  %s" % (dt, p, commands[p]))

    while len(pipes) < N_PROC and i < n_commands:
        logName = "Command_%03d.log" % (i)
        fLog = open(logName, 'w')
        arguments = ['srun', '--share', '-N1', '-n1']
        arguments.extend(commands[i].split())
        pipes[i] = subprocess.Popen(arguments, stdout = fLog, stderr=subprocess.STDOUT)
        dt = time.time() - start_time
        print("[%4d s] Started    %3d  %s" % (dt, i, commands[i]))
        i += 1
    
    time.sleep(1)

printLine()
print("Finished.")
printLine()
