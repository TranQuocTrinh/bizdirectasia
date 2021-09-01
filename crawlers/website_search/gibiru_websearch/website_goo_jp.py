import pandas as pd
import json
from bs4 import BeautifulSoup
from tqdm import tqdm
import sys
import time
import os
import ast
import requests


if not os.path.exists('./data_website/'):
    os.makedirs('./data_website/')
if not os.path.exists('./data_website/'+sys.argv[1].split('.csv')[0].split('_')[-1]):
    os.makedirs('./data_website/'+sys.argv[1].split('.csv')[0].split('_')[-1])

def extract_detail(soup):
    data = []
    i = 0
    for x in soup.findAll('div', class_='result'):
        try:
            temp = {}
            temp['title'] = x.find('a').getText(strip=True)
            temp['url'] = x.find('a')['href']
            temp['_index'] = i
            data.append(temp)
            i += 1
        except:
            pass
    return data

def search(company_name, company_id, company_key, country):
    countrys = {
        'indo': 'Indonesia',
        'korea': 'Korea',
        'hongkong': 'Hongkong',
        'taiwan':  'Taiwan'
    }
    search = company_name + countrys[country]
    rq_url = 'https://search.goo.ne.jp/web.jsp?MT='+search.replace(' ', '%20')+'&mode=0&sbd=goo001&IE=UTF-8&OE=UTF-8&from=s_b_top_web&PT=TOP'
    for i in range(20):
        try:
            r = requests.get(rq_url)
            break
        except:
            pass

    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')
        results = extract_detail(soup)
        data = {'company_id':company_id, 'company_key': company_key, \
                'company_name': company_name, 'results':results}
    
        return data, len(results), True
    else:
        print('status_code:', r.status_code)
        return {}, 0, False


def main():
    """
    sys.argv[1]:    file data
    sys.argv[2]:    number of proxy group
    sys.argv[3]:    end
    sys.argv[4]:    begin
    ##################### python  file_data   number_of_proxy_group   end   begin #####################
    """
    # read_csv
    file_data = sys.argv[1]
    country = file_data.split('.csv')[0].split('_')[-1]
    df = pd.read_csv(file_data)

    end = int(sys.argv[2])
    begin = int(sys.argv[3])

    count_block = 0
    for i in tqdm(range(len(df.company_id))):
        cp_id, cp_key, cp_name = str(df.company_id[i]), str(df.company_key[i]), \
                                        str(df.company_name[i])
        if i < begin or i > end:    # begin <= i <= end
            continue

        start_time = time.time()
        data, num_results, flag = search(cp_name, cp_id, cp_key, country)
        end_time = time.time()
        if flag == False:
            count_block += 1
            continue

        if num_results != 0 : #Co ket qua -> dump file
            file_name = './data_website/'+ country +'/'+ str(i)+'_'+cp_id.replace('/','-')+'.json'
            json.dump(data, open(file_name,'w'))
            count_block = 0
            # print('end =', end,'begin =', i, 'country =', sys.argv[1].split('.csv')[0].split('_')[-1], \
            # 'results =', num_results, 'time =', round(end_time-start_time,2), \
            # 'remainder =', end-i)
            print(data)
        else:
            count_block += 1
            if count_block > 5000:
                print('--------------BLOCK :)-------------\n--------------BLOCK :)-------------')
                break

if __name__ == '__main__':
    main()
