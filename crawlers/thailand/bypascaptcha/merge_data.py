import json
import pandas as pd
import os
from pandas.io.json import json_normalize
from tqdm import tqdm

folder = './data/'
names = os.listdir(folder)

data = []
for name in tqdm(names):
    try:
        data = data + json.load(open(folder+name))
    except:
        print(name)

data = data + json.load(open('part1.json'))
# delup
print('delup.....')
registered_no = []
data_fn = []
for d in tqdm(data):
    if d['registered_no.'] not in registered_no:
        registered_no.append(d['registered_no.'])
        data_fn.append(d)

json.dump(data_fn, open('company_name_thai.json','w'))
print(len(data_fn))
df = json_normalize(data_fn)
df.to_csv('company_name_thai.csv', index=False)
