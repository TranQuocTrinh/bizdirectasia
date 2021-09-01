# -*- coding: utf-8 -*-
import json
import os
import sys
from bs4 import BeautifulSoup
import pandas as pd 
from tqdm import tqdm
import pdb
import html2text

def par_name(name):
    temp = name
    temp = temp.replace('\n',' ').replace('*',' ').strip()
    temp = ' '.join(list(filter(lambda a: a!= '', temp.split(' '))))
    
    t = temp.split('BHD')
    if len(t) >= 2:
        temp = t[0] + 'BHD'
    t = temp.split('LTD')
    if len(t) >= 2:
        temp = t[0] + 'LTD'
    t = temp.split('LCC')
    if len(t) >= 2:
        temp = t[0] + 'LCC'
    temp = temp.split('ALL R')[0]
    temp = temp.split('(HTTP')[0]
    return temp


def extract(html):
    text = html2text.html2text(html).lower()
    index_1 = text.find('©')
    index_2 = text.find('copyright')
    index_3 = text.find('copyright ©')
    if index_3 != -1:
        index = index_3
    elif index_2 != -1:
        index = index_2
    else:
        index = index_1
    if index != -1:
        cp_name = text[index:index+100]
        cp_name = ' '.join(list(filter(lambda a: a != '', cp_name.upper().split('ALL R')[0].split(' '))))
        cp_name = par_name(cp_name)
    else:
        cp_name = ''
    return cp_name



path = sys.argv[1]
names = os.listdir(path)
url = []
extract_company_name = []
count = 0
for name in tqdm(names):
    print(name)
    print('load file')
    data = json.load(open(path + name))
    for k in tqdm(data.keys()):
        url.append(k)
        cp_name = extract(data[k])
        extract_company_name.append(cp_name)
        if cp_name != '':
            count += 1
            break
    break



df = pd.DataFrame({'url':url, 'extract_company_name':extract_company_name})
df.to_csv('extract_company_name.csv', index=False)
