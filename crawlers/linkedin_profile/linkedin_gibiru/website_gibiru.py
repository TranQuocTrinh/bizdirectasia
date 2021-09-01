import pandas as pd
import json
from bs4 import BeautifulSoup
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sys
import time
import os
import ast
import requests


if not os.path.exists('./data_website/'):
    os.makedirs('./data_website/')
if not os.path.exists('./data_website/'+sys.argv[1].split('.csv')[0].split('_')[-1]):
    os.makedirs('./data_website/'+sys.argv[1].split('.csv')[0].split('_')[-1])



def create_driver(address):
    # set hiden chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # set proxy
    options = webdriver.ChromeOptions()
    options.add_argument('--proxy-server=%s' % address)
    driver = webdriver.Chrome(options=options)#, chrome_options=chrome_options)

    driver.get('https://gibiru.com/')
    
    return driver

def extract_detail(soup):
    data = []
    i = 0
    for x in soup.findAll('a', class_='gs-title'):
        try:
            temp = {}
            temp['title'] = x.getText(strip=True)
            temp['url'] = x['href']
            temp['_index'] = i
            data.append(temp)
            i += 1
        except:
            pass
    return data

"""
def multi_page(driver):
    results = []
    results = results + extract_detail(BeautifulSoup(driver.page_source, 'html.parser'))
    for i in range(2, 11):
        try:
            driver.find_element_by_css_selector('#___gcse_0 > div > div > div > div.gsc-wrapper > div.gsc-resultsbox-visible > div.gsc-resultsRoot.gsc-tabData.gsc-tabdActive > div > div.gsc-cursor-box.gs-bidi-start-align > div > div:nth-child('+str(i)+')').click()
            time.sleep(0.5)
        except:
            break
        len_temp = len(results)
        results = results + extract_detail(BeautifulSoup(driver.page_source, 'html.parser'))
        if len(results) == len_temp:
            break
    return results
"""

def search(driver, company_name, company_id, company_key):
    search = company_name + '\n'
    try:
        css_selector = '#q'
        driver.find_element_by_css_selector(css_selector).clear()
        driver.find_element_by_css_selector(css_selector).send_keys(search)
    except:
        css_selector = '#q'
        driver.find_element_by_css_selector('#cse-search-box > div > span').click()
        driver.find_element_by_css_selector(css_selector).send_keys(search)
    time.sleep(0.5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # results = multi_page()
    results = extract_detail(BeautifulSoup(driver.page_source, 'html.parser'))
    data = {'company_id':company_id, 'company_key': company_key, 'company_name': company_name, 'results':results}
    
    return data, len(results)

proxies = ast.literal_eval(requests.get('http://68.183.229.8:9069/proxy/list').text)
proxies = [ip + ':3128' for ip in proxies]
proxy_th = int(sys.argv[2])
driver = create_driver(proxies[proxy_th])

df = pd.read_csv(sys.argv[1])
end = int(sys.argv[3])
begin = int(sys.argv[4])

count_block = 0
for i in range(len(df.company_id)):
    cp_id, cp_key, cp_name = str(df.company_id[i]), str(df.company_key[i]), str(df.name[i])
    if i >= begin and cp_name != 'nan' and i <= end:
        #try:
        start_time = time.time()
        data, num_results = search(driver, cp_name, cp_id, cp_key)
        end_time = time.time()
        if num_results !=0 : #Co ket qua -> dump file
            print('co result')
            json.dump(data, open('./data_website/'+sys.argv[1].split('.csv')[0].split('_')[-1]\
                    +'/'+ str(i)+'_'+cp_id.replace('/','-')+'.json','w'))
            print('end =', end,'begin =', i, 'country =', sys.argv[1].split('.csv')[0].split('_')[-1], \
                'results =', num_results, 'time =', round(end_time-start_time,2), \
                'remainder =', end-i)
            count_block = 0
        else: # kiem tra block
            count_block +=1
            print('khong result')
            print('end =', end,'begin =', i, 'count_block =', count_block, \
                'time =', round(end_time-start_time,2), 'remainder =', end-i)
            if count_block > 1000:
                print('BLOCK_IP!!!')
                #driver = create_driver(proxies[proxy_th+1])
                #proxy_th += 1
                break
        time.sleep(0.5)
        #except:
        #    pass

