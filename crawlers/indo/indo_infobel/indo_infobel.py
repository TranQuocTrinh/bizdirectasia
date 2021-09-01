import requests
import time
import json
import os
import sys
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm

categories_lv1 = json.load(open('cate_and_url_use_run.json'))

def extract_data_company(r):
    soup = BeautifulSoup(r.text, 'html.parser')
    div = soup.find('div',class_='customer-item-info')
    name = div.find('h2').get_text()
    address =  div.find('span').get_text()
    phone = [x.get_text() for x in div.find('div', style='display:none').find_all('span') if x.get_text()!='']
    try:
        website = div.find('a', rel='noopener external')['href']
    except:
        website = ''
    data = {'company_name':name, 'address':address, 'phone_number': phone, 'website':website}
    return data

categories_lv1_temp = categories_lv1
for cate_1 in tqdm(categories_lv1):
    for link in tqdm(categories_lv1[cate_1]):
        for page in tqdm(range(1,50)):
            if page >= int(sys.argv[1]):
                page = str(page)
                if page != '1':
                    url = link + '/'+str(page)
                else:
                    url = link
                r = requests.get(url)
                if r.url != url:
                    break
                else:
                    soup = BeautifulSoup(r.text, 'html.parser')
                    url_companies_in_page = ['https://www.infobel.com'+x.find('a')['href'] for x in soup.findAll('h2', class_='customer-item-name')]
                    for url_company in tqdm(url_companies_in_page):
                        data = extract_data_company(requests.get(url_company))
                        data['page'] = page
                        data['categories_lv1'] = cate_1
                        data['categories_lv2'] = link.split('/')[-1]
                        data['catagories_lv2_code'] = link.split('/')[-2]
                        #print(data)
                        json.dump(data, open('data/'+data['company_name'].replace(' ','_').replace('/','-')+'_'+page+'_.json','w'))
                        time.sleep(4)
        json.dump(categories_lv1_temp[cate_1].remove(link),open('cate_and_url_use_run.json','w'))