import json
import pandas as pd
import sys
import os
from tqdm import tqdm

#folders = ['thailand', 'brunei', 'laos', 'singapore', 'philippines', 'cambodia', 'myanmar', 'malaysia'] #'vietnam', 'indonesia']

def delup(data):
    company_key_temp = list(data.company_key)
    company_id_temp = list(data.company_id)
    search_temp = list(data.search)
    title_temp = list(data.title)
    url_temp = list(data.url)
    order_temp = list(data.order)
    url_temp = ['/'.join(x.split('/')[:3]) for x in url_temp]
    url_uni = list(set(url_temp))
    print(len(url_uni))
    search = title = url = company_key = company_id = order = []
    for x in tqdm(url_uni):
        index = url_temp.index(x)
        url.append(x)
        search.append(search_temp[index])
        title.append(title_temp[index])
        company_id.append(company_id_temp[index])
        company_key.append(company_key_temp[index])
        order.append(order_temp[index])
    df = pd.DataFrame({'search':search, 'title':title, 'url':url})
    df = pd.DataFrame({"company_id":company_id,"company_key":company_key,"search":search, "title":title, "url":url, "order":order})
    #df.to_csv(folder+'_delup.csv', index=False)
    return df


folders = [sys.argv[1]]
for folder in folders:
    names = os.listdir('data_company/'+folder+'/')
    search = title = url = company_key = company_id = order = []
    for name in tqdm(names):
        data = json.load(open("./data_company/"+folder+"/"+name))
        for i, d in enumerate(data["results"]):
            #if d["url"] not in url:
            search.append(data["search"])
            title.append(d["title"])
            url.append(d["url"])
            company_key.append(data["company_key"])
            company_id.append(data["company_id"])
            order.append(d["order"])

    df = pd.DataFrame({"company_id":company_id,"company_key":company_key,"search":search, "title":title, "url":url, "order":order})
    # call delup
    df = delup(df)
    df.to_csv('data_csv_delup/'+folder+"_delup.csv", index=False)
    print(folder)
