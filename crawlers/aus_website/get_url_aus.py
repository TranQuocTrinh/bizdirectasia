import requests
import pandas as pd
import json
import time
from tqdm import tqdm
from bs4 import BeautifulSoup
import sys
import os

if not os.path.exists('./data_web_aus/'):
    os.makedirs('./data_web_aus/')

link = json.load(open('link_lv_2.json'))
count = 0
for l in tqdm(link):
    if count >= int(sys.argv[1]):
        for i in tqdm(range(1, 100)):
            if (count == int(sys.argv[1]) and i>= int(sys.argv[2])) or count > int(sys.argv[1]):
                l = l.split('p=')[0]+'p='+str(i)+'&dst'+l.split('p=')[-1].split('&dst')[-1]
                r = requests.get(l)
                if r.status_code != 200:
                    print('STATUS CODE != 200')
                    exit()
                page = str(i)
                req_page = r.url.split('p=')[-1].split('&dst')[0]
                if page != req_page:
                    break
                else:
                    soup = BeautifulSoup(r.text, 'html.parser')
                    item = soup.find_all('div', style='display:table-cell; width:auto; vertical-align:top; line-height:1.4')
                    names = [x.find('a').get_text() for x in item]
                    website = []
                    for x in item:
                        try:
                            website.append(x.find_all('a')[2].get_text())
                        except:
                            website.append(x.find_all('a')[1].get_text())
                    city = ' '.join(l.split('c=')[-1].split('&z=')[0].split('-')).upper()
                    data = []
                    for name, web in zip(names, website):
                        data.append({'url':l, 'name': name, 'website': web, 'city': city, 'page': i})
                    json.dump(data,open('./data_web_aus/'+city+'_page '+page+'.json','w'))
                    time.sleep(10)
        count += 1
        time.sleep(10)
