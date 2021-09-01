import json
import pandas as pd
import sys
import os
from tqdm import tqdm

#folders = ['thailand', 'brunei', 'laos', 'singapore', 'philippines', 'cambodia', 'myanmar', 'malaysia'] #'vietnam', 'indonesia']

folders = [sys.argv[1]]

for folder in folders:
    names = os.listdir(folder)
    search = []
    title = []
    url = []
    content = []
    company_id = []
    for name in tqdm(names):
        data = json.load(open(folder+"/"+name))
        for i, d in enumerate(data["results"]):
            x = '/'.join(d["url"].split("/")[:3])
            if x not in url:
                search.append(data["search"])
                title.append(d["title"])
                url.append(x)
                content.append(d["content"])
                company_id.append(data["index"])
    df = pd.DataFrame({"index":company_id, "company_name":search, "title":title, "url":url})
    df.to_csv("indo_yahoo_delup.csv", index=False)
