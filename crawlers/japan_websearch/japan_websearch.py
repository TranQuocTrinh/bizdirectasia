from bs4 import BeautifulSoup
import time
import json
import pandas as pd
import sys
import os
import requests
from tqdm import tqdm

class SW:
    def __init__(self):
        self.url = 0

    def search(self, company_name, company_id):
        search = '会社概要'+company_name

        data = {"search":search,"company_id":str(company_id)}
        results = self.get_detail(search)
        data["results"] = results
        return data

    def get_detail(self,search):  #.co.jp/sear
        #url = 'https://search.yahoo.com/search?p=+'+search+'&aq=-1&oq=&ai=HT0uxzLFTwusl.qzKoDY8A&ts=1498&ei=UTF-8&fr=sfp_as&x=wrt'
        #url = 'https://search.yahoo.com/search;_ylt==Awr9DuKfYqFdTQUAoX9DDWVH?&p='+search+'fr=sfp&iscqry='
        url = 'https://search.yahoo.com/search;_ylt=Awr9DuKfYqFdTQUAoX9DDWVH?p='+search+'&fr=sfp&iscqry='
        r = requests.get(url)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser').find('div', id='web')
            url = [x['href'] for x in soup.find_all('a')]
            title = [x.get_text() for x in soup.find_all('a')]

            results = []
            for i in range(len(url)):
                temp = {}
                temp['title'] = title[i]
                temp['url'] = url[i]
                temp['order'] = str(i)
                results.append(temp)
        else:
            print('Get URL error!!!')
            return []
        return results

path = './data_japan/jp_process_'+sys.argv[1]+'.csv'
def read_csv(path):
    print('load data....')
    df = pd.read_csv(path)
    return list(df['company_id']), list(df['tradestyle'])
company_id, company_name = read_csv(path)
if len(sys.argv) == 4:
    end_skip = int(sys.argv[2])
    skip = int(sys.argv[3])
elif len(sys.argv) == 3:
    skip = int(sys.argv[2])
    end_skip = len(company_name)
elif len(sys.argv) == 2:
    skip = 0
    end_skip = len(company_name)


ob = SW()
solanchan = 0
for i in tqdm(range(len(company_name))):
    if i >= skip and i < end_skip:
        check_blocking = 0
        while True:
            data = ob.search(company_name[i],company_id[i])
            json.dump(data,open('./data_websearch/'+'jp_'+sys.argv[1]+'_'+str(company_id[i])+'_'+str(i)+'.json','w'))
            if data["results"] == []:
                check_blocking += 1
            else:
                check_blocking = 0
                break

            if check_blocking >= 10:
                print("CHAN!!!")
                solanchan += 1
                break
        if solanchan >= 10:
            break

