import pandas as pd
import json
import os
from tqdm import tqdm

key = json.load(open('data/1.json'))[0].keys()
#df = pd.DataFrame()#columns=list(key))
dct = {}
for k in key:
    dct[k] = []

#index = 0
names = os.listdir('data')
for name in tqdm(names):
    dt = json.load(open('data/'+name))
    for x in dt:
        x['index'] = int(x['index'])
        #df.loc[index] = list(x.values())
        for k in x.keys():
            dct[k].append(x[k])
        #index += 1
df = pd.DataFrame(dct)
df = df.sort_values(by = 'index')
df.to_csv('indo_beritanegara.csv',index=False)
