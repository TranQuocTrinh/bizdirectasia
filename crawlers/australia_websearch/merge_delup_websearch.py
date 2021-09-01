import json
import pandas as pd
import sys
import os
from tqdm import tqdm

folders = [sys.argv[1]]

for folder in folders:
    names = os.listdir(folder)
    search = []
    title = []
    url = []
    company_id = []
#    company_key = []
    dct = {}
    for name in tqdm(names):
        data = json.load(open(folder+"/"+name))
        for i, d in enumerate(reversed(data["results"])):
            x = '/'.join(d["url"].split("/")[:3])
            #if x not in url:
            dct[x] = (data['search'], d['title'], data['company_id'])
            #search.append(data["search"])
            #title.append(d["title"])
            #url.append(x)
#                content.append(d["content"])
            #company_id.append(data["company_id"])
#                company_key.append(data["company_key"])
    #set_url = list(set(url))

    search_ = []
    title_ = []
    company_id_ = []
    for k in tqdm(dct):
        search_.append(dct[k][0])
        title_.append(dct[k][1])
        company_id_.append(dct[k][2])

    df = pd.DataFrame({"company_id":company_id_, "search":search_, "title":title_, "url":list(dct.keys())})
    df.to_csv("data_csv_delup/aus_yahoo_delup.csv", index=False)
    print(folder)
