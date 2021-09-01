import sys
import json
import requests
import pandas as pd
import time
from tqdm import tqdm
from bs4 import BeautifulSoup

def proxy_dict(ip):
    http_proxy  = "http://" + ip + ":3128"
    https_proxy = "https://" + ip + ":3128"
    ftp_proxy   = "ftp://" + ip + ":3128"
    proxyDict = {
                  "http"  : http_proxy,
                  "https" : https_proxy,
                  "ftp"   : ftp_proxy
                }
    return proxyDict

def extract_detail(soup):
    data = {'company_name': soup.find('h1', class_='single-company__hero-name').getText()}
    for x in soup.findAll('div', class_='company-profile__item'):
        data[x.find('div').getText().lower().replace(' ','_')] = x.findAll('p')[-1].getText()

    for x in soup.findAll('div', class_='general-info__item'):
        data[x.find('p').getText().lower().replace(' ','_')] = x.findAll('p')[-1].getText()

    for x in soup.findAll('div', class_='industry__item'):
        data[x.find('p').getText().lower().replace(' ','_')] = x.findAll('p')[-1].getText()

    try:
        temp = soup.find('table', class_='table capital__table')
        for x, y in zip(temp.findAll('th'), temp.findAll('td')):
            data[x.getText().lower().replace(' ', '_')] = y.getText()
    except:
        pass

    return data

import ast

ips = ast.literal_eval(requests.get('http://68.183.229.8:9069/proxy/list?group=1').text)
ip = ips[0]

urls = json.load(open('./urls.json'))
begin = int(sys.argv[1])
for i in tqdm(range(len(urls))):
    if i >= begin:
        count = 0
        url = urls[i]
        while True:
            try:
                data = extract_detail(BeautifulSoup(requests.get(url, proxies=proxy_dict(ip)).text,'html.parser'))
                json.dump(data, open('data/'+data['company_name']+data['registration_number']+'.json', 'w'))
                break
            except:
                if len(ips) > 1:
                    ips.remove(ip)
                else:
                    count += 1
                    if count >= 3:
                        break
                    print('waiting...')
                    requests.get('http://68.183.229.8:9069/proxy/renew?group=1')
                    time.sleep(600)
                    ips = ast.literal_eval(requests.get('http://68.183.229.8:9069/proxy/list?group=1').text)

                ip = ips[0]
