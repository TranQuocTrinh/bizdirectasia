import json
import sys
from pprint import pprint

folders = []
for i in range(0,12):
    folders.append("data"+str(i)+"/")

d = 0
for folder in folders:
    f = open(folder+"/ls.txt")
    names = f.readlines()
    names = [x[:-1] for x in names]

    set_names = []
    names2 = []
    for name in names:
        set_names.append(name[-4:])
        if name[-4:] == "json":
            names2.append(name)

    #print(set(set_names))

    company_status = []
    for name in names2:
        data = json.load(open(folder+"/"+name))
        if data["tabs"][0]["value"]["company_status"] == "ยังดำเนินกิจการอยู่":
            d += 1
        company_status.append(data["tabs"][0]["value"]["company_status"])
print(d)
    #print(set(company_status))
    #print(len(set(company_status)))
