import pandas as pd
import json
import csv
import time
from tqdm import tqdm
import sys
import os

dir_name = sys.argv[1]
names = os.listdir(dir_name)

company_names = []
company_ids = []
company_keys = []
urls = []
indexes = []

for name in tqdm(names):
    data = json.load(open(os.path.join(dir_name, name)))
    for r in data['results']:
        company_ids.append(data['company_id'])
        company_keys.append(data['company_key'])
        company_names.append(data['company_name'])
        urls.append(r['url'])
        indexes.append(r['_index'])

df = pd.DataFrame({'company_id': company_ids, 'company_key':company_keys, 'company_name': company_names, 'url':urls, 'index': indexes})

try:
    name_f = os.path.join(dir_name.split('/')[0], 'all_data_website_search_' + dir_name.split('/')[-2] +'.csv')
    print(name_f)
except:
    name_f = 'all_data.csv'
    print('File name have a bug. Waining!!!')

df.to_csv(name_f, index=False)
