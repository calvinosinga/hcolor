import pickle as pkl
import sys

pklpath = sys.argv[1]
f = pkl.load(open(pklpath, 'rb'))
print(f.getQueue())
queue = f.getQueue()
for q in queue:
    print('JOBNAME: ')
    print(q.getJobName())
    print('COMMAND: ')
    print(q.getCmd())
