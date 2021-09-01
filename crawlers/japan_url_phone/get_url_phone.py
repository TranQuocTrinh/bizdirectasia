import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import json

def get_url_phone(company_id):
    data = {'company_id': company_id}
    url = 'https://xn--gmqp1kvuze1h.com/?corporate_no='+company_id
    r = requests.get(url)
    if r.status_code != 200:
        return False
    soup = BeautifulSoup(r.text, 'html.parser')
    #check false
    try:
        if soup.find('h2', id='h1_txt2').find('p').get_text() == 'この法人番号は存在しません。':
        #return data
            print('This corporation number does not exist!')
            pass
    except:
        table = soup.find('tbody', class_='table-bordered').find_all('tr')
        for tr in table:
            td = [x.get_text().strip() for x in tr.find_all('td')]
            if td[0] == '電話番号':
                data['phone_number'] = td[1].replace('\xa0\xa0変更送信 \xa0\xa0削除','').replace("登録送信",'')
            if td[0] == 'URL':
                data['url'] = td[1].replace('\xa0\xa0変更送信 \xa0\xa0削除','').replace("登録送信",'')

    return data

import sys
company_ids = pd.read_csv('japan_id/jp_id+'+sys.argv[1]+'.csv').company_id.astype('str')

if len(sys.argv) == 2:
    start = 0
    end = len(company_ids)
if len(sys.argv) == 3:
    start = int(sys.argv[1])
    end = len(company_ids)
if len(sys.argv) == 4:
    start = int(sys.argv)[3]
    end = int(sys.argv)[2]

for i in tqdm(range(len(company_ids))):
    if i >= start <= end:
        data = get_url_phone(company_ids[i])
        if data:
            if data['url'] != '' or data['phone_number'] != '':
                json.dump(data, open('data_jp_url_phone/'+sys.argv[1]+'_'+company_ids[i]+'.json','w'))
        else:
            print('status code != 200')
            break
