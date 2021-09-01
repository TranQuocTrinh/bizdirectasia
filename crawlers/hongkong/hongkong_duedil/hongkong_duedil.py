import requests
from bs4 import BeautifulSoup
import json
import sys
from tqdm import tqdm


def extract_detail_company(soup):
    data = {}
    dls = soup.findAll('dl', class_='entity-attributes')
    dt = []
    dd = []
    for dl in dls:
        dt = dt + [x.getText(strip=True).strip('\n') for x in dl.findAll('dt')]
        dd = dd + [x.getText(strip=True).strip('\n') for x in dl.findAll('dd')]

    data = {x.lower().replace(' ','_'):y for x,y in zip(dt,dd)}
    return data

if len(sys.argv) == 1:
    begin = 0
    end = 10000000
if len(sys.argv) == 2:
    begin = int(sys.argv[1])
    end = 10000000
if len(sys.argv) == 3:
    begin = int(sys.argv[2])
    end = int(sys.argv[1])

count = 0

for i in tqdm(range(begin, end)):
    id_ = str(i)
    while len(id_) != 7: 
        id_ = '0' + id_ 
    r = requests.get('https://www.duedil.com/company/hk/'+id_) 
    soup = BeautifulSoup(r.text, 'html.parser') 
    check = soup.find('h1').getText(strip=True)
    if check != '404: Not Found':
        count += 1
        company_name = soup.find_all('h1')[1].getText(strip=True)
        data = extract_detail_company(soup)
        print(data)
        print("Count = ", count, "\t And have/ haven't is", count/(i+1)*100, '\t begin =', i, 'end =', end)
        json.dump(data, open('data_hongkong_duedli/'+id_+'.json','w'))
