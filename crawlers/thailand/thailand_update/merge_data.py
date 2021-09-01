import json
import os
import sys
from tqdm import tqdm

folder = sys.argv[1]
names = os.listdir(folder)

all_data = []
for name in tqdm(names):
    data = json.load(open(folder+name))
    if data['total_revenue'][0]['year'] != '':
    #temp_data = {}
    #temp_data['registration_tax'] = data['registration_tax']
    #temp_data['total_revenue'] = []
    #for i,temp in enumerate(data['total_revenue']):
    #    if temp['year'] == "":
    #        temp['year'] = str(2016+i)
    #    temp_data['total_revenue'].append(temp)
        all_data.append(data)
print(len(all_data))
json.dump(all_data, open('thailan_revenue.json','w'))
