import json
import sys
import os
import shutil

names = open(sys.argv[1]+"ls.txt").read().strip().split("\n")
names.remove("ls.txt")
# find file bug
bug = []
for name in names:
    data = open(sys.argv[1]+name).read()
    data = json.loads(json.loads(data))
    if len(data["queries"]["request"][0]["title"].split('"')) == 2:
        bug.append(name)

print(len(bug), len(names))
print(len(bug)/len(names))

# move file bug to folder bugfile
for b in bug:
    try:
        os.rename(sys.argv[1]+b, sys.argv[2]+b)
        shutil.move(sys.argv[1]+b, sys.argv[2]+b)
    except:
        pass
