f = open("com_swanson.txt", "w")
h = open("com_nelson.txt", "w")
SNAPSHOT = '99'

fileno = 4
for i in range(fileno):
    if i==fileno-1:
        f.write("python3 /lustre/cosinga/hcolor/hisubhalo/swanson.py " +str(i) + ' '+ SNAPSHOT)
    else:
        f.write("python3 /lustre/cosinga/hcolor/hisubhalo/swanson.py "+str(i)+' '+SNAPSHOT+"\n")

for i in range(fileno):
    if i==fileno-1:
        h.write("python3 /lustre/cosinga/hcolor/hisubhalo/nelson.py " +str(i) + ' '+ SNAPSHOT)
    else:
        h.write("python3 /lustre/cosinga/hcolor/hisubhalo/nelson.py "+str(i)+' '+SNAPSHOT+"\n")
