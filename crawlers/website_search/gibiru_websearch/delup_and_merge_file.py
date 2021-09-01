import json
import os
from tqdm import tqdm
import sys
import time 
import pandas as pd


path = sys.argv[1]
dst = sys.argv[2]
print('Delup and move file to new folder.......!')
for name in tqdm(os.listdir(path)):
    data = json.load(open(path + name))
    results = []
    url = set()
    index = 0
    for r in data['results']:
        new_url = '/'.join(r['url'].split('/')[:3])
        if new_url not in url:
            url.add(new_url)
            r['_index'] = index
            r['url'] = new_url
            index += 1
            results.append(r)
    data['results'] = results

    json.dump(data, open(dst + name, 'w'))
    #os.remove(path + name)
print(len(os.listdir(dst)))



# merge file to csv
print('Merge file to csv...............!')
dir_name = dst #sys.argv[1]
names = os.listdir(dir_name)

company_names = []
company_ids = []
company_keys = []
urls = []
indexs = []
titles = []

for name in tqdm(names):
    data = json.load(open(dir_name+name))
    for r in data['results']:
        company_ids.append(data['company_id'])
        company_keys.append(data['company_key'])
        company_names.append(data['company_name'])
        urls.append(r['url'])
        titles.append(r['title'])
        indexs.append(r['_index'])

df = pd.DataFrame({'company_id': company_ids, 'company_key':company_keys, 'company_name': company_names, 'url':urls, 'title': titles, 'index': indexs})

try:
    name_f = dir_name.split('/')[0] + '/all_data_website_search_' + dir_name.split('/')[-2] +'.csv'
    print(name_f)
except:
    name_f = 'all_data_.csv'
    print('name file bug. Waining!!!')

df.to_csv(name_f, index=False)
