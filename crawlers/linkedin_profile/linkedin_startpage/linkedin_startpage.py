import pandas as pd
import json
from bs4 import BeautifulSoup
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sys
import time
import os

if not os.path.exists('./data_linkedin/'):
    os.makedirs('./data_linkedin/')
if not os.path.exists('./data_linkedin/'+sys.argv[1].split('.csv')[0].split('_')[-1]):
    os.makedirs('./data_linkedin/'+sys.argv[1].split('.csv')[0].split('_')[-1])

# set hiden chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(chrome_options=chrome_options)
driver.get('https://www.startpage.com/')

def extract_detail(soup):
    data = []
    for x in soup.findAll('a', class_='w-gl__result-title'):
        try:
            temp = {}
            temp['title'] = x.getText(strip=True)
            temp['url'] = x['href']
            data.append(temp)
        except:
            pass
    return data

def multi_page():
    results = []
    for i in range(1, 11):
        try:
            driver.find_element_by_css_selector('body > div.layout > div > div.layout-web__body > div.layout-web__mainline > div.show-when-ads-load > div.pagination.pagination--default.pagination--desktop > form > button').click()
            time.sleep(1)
        except:
            break
        len_temp = len(results)
        results = results + extract_detail(BeautifulSoup(driver.page_source, 'html.parser'))
        if len(results) == len_temp:
            break
    return results

def search(company_name, company_id, company_key):
    search = '"- ' + company_name +'" site:linkedin.com/in\n'
    try:
        css_selector = '#q'
        driver.find_element_by_css_selector(css_selector).clear()
        driver.find_element_by_css_selector(css_selector).send_keys(search)
    except:
        css_selector = '#query'
        driver.find_element_by_css_selector(css_selector).clear()
        driver.find_element_by_css_selector(css_selector).send_keys(search)
    time.sleep(1)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    results = multi_page()
    return {'company_id':company_id, 'company_key': company_key, 'company_name': company_name, 'results':results}

df = pd.read_csv(sys.argv[1])
begin = int(sys.argv[2])

count_block = 0
for i in range(len(df.company_id)):
    cp_id, cp_key, cp_name, trade_name = str(df.company_id[i]), str(df.company_key[i]), \
            str(df.company_name[i]), str(df.trade_style_name[i])

    if i >= begin and cp_name != 'nan':
        if trade_name == 'nan':
            trade_name = cp_name
        start_time = time.time()
        data = search(trade_name, cp_id, cp_key)
        end_time = time.time()
        if len(data['results']) !=0 :
            json.dump(data, open('./data_linkedin/'+sys.argv[1].split('.csv')[0].split('_')[-1]\
                    +'/'+ cp_id.replace('/','-')+'_'+cp_key.replace('/','-')+'.json','w'))
            print('begin =', i, 'country =', sys.argv[1].split('.csv')[0].split('_')[-1], \
                    'results =', len(data['results']), 'time =', end_time-start_time, \
                    'remainder =', len(df.company_id)-i, \
                    'percent =', float(i)/len(df.company_id)*100,\
                    'search = ' + '"- ' + trade_name +'" site:linkedin.com/in' )
            count_block = 0
        else:
            count_block +=1
            print('begin =', i,'country =', sys.argv[1].split('.csv')[0].split('_')[-1],\
                    'count_block =', count_block, 'remainder =', len(df.company_id)-i, \
                    'search = ' + '"- ' + trade_name +'" site:linkedin.com/in')
            if count_block > 500:
                print('BLOCK_IP!!!')
                break
        time.sleep(1)
