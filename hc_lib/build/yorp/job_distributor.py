#!/bin/env python


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
import psutil
import pickle as pkl
import sys

########################################################################################################

def printLine():
    print('--------------------------------------------------------------')
    return

########################################################################################################

printLine()
print("Welcome to the job distributor.")
printLine()

start_time = time.time()

prefix = sys.argv[1]

# Find commands to execute
jm = pkl.load(open(prefix + '_job_manager.pkl', 'rb'))
queue = jm.getQueue()
n_commands = len(queue)
N_PROC = psutil.cpu_count()
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
            print("[%4d s] Completed  %3d  %s" % (dt, p, queue[p].getJobName()))

    while len(pipes) < N_PROC and i < n_commands:
        logName = "%s.log" % (queue[i].getJobName())
        fLog = open(logName, 'w')
        arguments = queue[i].getCmd()
        pipes[i] = subprocess.Popen(arguments, stdout = fLog, stderr=subprocess.STDOUT)
        dt = time.time() - start_time
        print("[%4d s] Started    %3d  %s" % (dt, i, queue[i].getJobName()))
        i += 1
    
    time.sleep(1)

printLine()
print("Finished.")
printLine()
