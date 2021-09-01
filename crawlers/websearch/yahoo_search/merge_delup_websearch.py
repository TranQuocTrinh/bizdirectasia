import json
import pandas as pd
import sys
import os
from tqdm import tqdm

#folders = ['thailand', 'brunei', 'laos', 'singapore', 'philippines', 'cambodia', 'myanmar', 'malaysia'] #'vietnam', 'indonesia']

folders = [sys.argv[1]]

for folder in folders:
    names = os.listdir('data_company/'+folder+'/')
    search = []
    title = []
    url = []
    content = []
    company_id = []
    company_key = []
    for name in tqdm(names):
        data = json.load(open("./data_company/"+folder+"/"+name))
        for i, d in enumerate(data["results"]):
            x = '/'.join(d["url"].split("/")[:3])
            if x not in url:
                search.append(data["search"])
                title.append(d["title"])
                url.append(x)
                content.append(d["content"])
                company_id.append(data["company_id"])
                company_key.append(data["company_key"])
    df = pd.DataFrame({"company_id":company_id, "company_key":company_key, "search":search, "title":title, "url":url})
    df.to_csv('data_csv_delup/'+folder+"_yahoo_delup.csv", index=False)
    print(folder)
