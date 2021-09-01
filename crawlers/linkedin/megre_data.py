import pandas as pd
import json
import os
import sys
from tqdm import tqdm

folder = sys.argv[1]
names = os.listdir('./data/'+folder)

company_id = []
company_name = []
company_key = []
title = []
url = []
index = []
prf_name = []
position = []

for name in tqdm(names):
    try:
        data = json.load(open('./data/'+folder+'/'+name))
    except:
        print(name)
        continue
    for d in data:
        if d['url'] not in url:
            company_id.append(d['company_id'])
            company_key.append(d['company_key'])
            company_name.append(d['company_name'])
            #title.append(d['title'])
            prf_name.append(str(d['title']).split('-')[0])
            try:
                position.append('-'.join(str(d['title']).split('-')[1:]))
            except:
                position.append('')
            url.append(d['url'])
            index.append(d['index'])

df = pd.DataFrame({'company_id':company_id,'company_key':company_key,'company_name':company_name,'name':prf_name,'position':position,'url':url,'index':index})
df.to_csv('./data/linkedin_profile_'+folder+'.csv', index=False)
