import sys
fileno = int(sys.argv[1])
f = open("commands_hiptl.txt",'w')
for i in range(int(fileno)):
    if i==fileno-1:
        f.write("python3 /lustre/cosinga/hcolor/hiptl/hiptl.py "+str(i))
    else:
        f.write("python3 /lustre/cosinga/hcolor/hiptl/hiptl.py "+str(i)+"\n")

