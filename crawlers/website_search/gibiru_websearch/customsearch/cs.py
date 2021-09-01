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

import ast
import requests
import random


def create_driver(url='https://cse.google.com/cse?cx=001394533911082033616:3rmgu_htqw4'):
    # set hiden chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # set proxy
    # options = webdriver.ChromeOptions()
    # options.add_argument('--proxy-server=%s' % address)

    driver = webdriver.Chrome(chrome_options=chrome_options)#,options=options)

    driver.get(url)
    time.sleep(2)
    return driver

def extract_detail(soup):
    data = []
    i = 0
    for x in soup.findAll('div', class_='gsc-thumbnail-inside'):
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

def search(driver, company_name, company_id, company_key, country):
    countrys = {
        'indo': 'Indonesia',
        'korea': 'Korea',
        'hongkong': 'Hongkong',
        'taiwan':  'Taiwan'
    }
    search = company_name + countrys[country] + '\n'
    flag_search = False
    for i in range(20):
        try:
            css_selector = '#gsc-i-id1'
            driver.find_element_by_css_selector(css_selector).clear()
            driver.find_element_by_css_selector(css_selector).send_keys(search)
            flag_search = True
            break
        except:
            pass
    
    if flag_search == False:
        for i in range(20):
            try:
                css_selector = '#gsc-i-id1'
                driver.find_element_by_css_selector(css_selector).clear()
                driver.find_element_by_css_selector(css_selector).send_keys(search)
                flag_search = True
                break
            except:
                pass

    if flag_search:
        time.sleep(0.5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # results = multi_page()
        results = extract_detail(soup)
        data = {'company_id':company_id, 'company_key': company_key, \
                'company_name': company_name, 'results':results}
    
        return data, len(results), True
    else:
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
    
    #create driver
    driver = create_driver()#'https://search.goo.ne.jp/')

    count_block = 0
    count_requests = 1  # 100 requests/proxy
    for i in tqdm(range(len(df.company_id))):
        cp_id, cp_key, cp_name = str(df.company_id[i]), str(df.company_key[i]), \
                                        str(df.company_name[i])
        if i < begin or i > end:    # begin <= i <= end
            continue

        start_time = time.time()
        data, num_results, flag = search(driver, cp_name, cp_id, cp_key, country)
        end_time = time.time()
        if flag == False:
            print('driver is false')
            driver.close()
            driver = create_driver()#'https://search.goo.ne.jp/')
            count_block += 1
            continue

        if num_results != 0 : #Co ket qua -> dump file
            file_name = './data_website/'+ country +'/'+ str(i)+'_'+cp_id.replace('/','-')+'.json'
            json.dump(data, open(file_name,'w'))
            count_block = 0
            print(data['results'])
            # print('end =', end,'begin =', i, 'country =', sys.argv[1].split('.csv')[0].split('_')[-1], \
            # 'results =', num_results, 'time =', round(end_time-start_time,2), \
            # 'remainder =', end-i)
        else:
            print('no results')
            count_block += 1
            if count_block > 5000:
                print('--------------BLOCK :)-------------\n--------------BLOCK :)-------------')
                break
    driver.close()

if __name__ == '__main__':
    main()
