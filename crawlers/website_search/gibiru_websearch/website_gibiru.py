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
    driver = webdriver.Chrome(options=options, chrome_options=chrome_options)

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

def search(driver, company_name, company_id, company_key, country):
    countrys = {
        'indo': 'Indonesia',
        'korea': 'Korea',
        'hongkong': 'Hongkong',
        'taiwan':  'Taiwan'
    }
    search = company_name + countrys[country] + '\n'
    for i in range(20):
        try:
            css_selector = '#q'
            driver.find_element_by_css_selector(css_selector).clear()
            driver.find_element_by_css_selector(css_selector).send_keys(search)
            break
        except:
            pass

    if i < 19:
        time.sleep(0.5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # results = multi_page()
        results = extract_detail(BeautifulSoup(driver.page_source, 'html.parser'))
        data = {'company_id':company_id, 'company_key': company_key, \
                'company_name': company_name, 'results':results}
    
        return data, len(results), True
    else:
        return {}, 0, False


def get_proxies(group_proxy_th):
    proxies = ast.literal_eval(requests.get('http://68.183.229.8:9069/proxy/list?group='+group_proxy_th).text)
    proxies = [ip + ':3128' for ip in proxies]
    return proxies

def renew_proxies(group_proxy_th):
    requests.get('http://68.183.229.8:9069/proxy/renew?group='+group_proxy_th)
    time.sleep(100)


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

    end = int(sys.argv[3])
    begin = int(sys.argv[4])
    group_proxy_th = sys.argv[2]
    
    #create driver
    proxies = get_proxies(group_proxy_th)
    proxy_th = 0
    driver = create_driver(proxies[proxy_th])

    count_block = 0
    count_requests = 1  # 100 requests/proxy
    for i in tqdm(range(len(df.company_id))):
        cp_id, cp_key, cp_name = str(df.company_id[i]), str(df.company_key[i]), \
                                        str(df.company_name[i])
        if i < begin or i > end:    # begin <= i <= end
            continue

        if count_requests % 150 == 0:   # switch proxy
            proxy_th += 1
            if proxy_th == len(proxies):
                renew_proxies(group_proxy_th)
                proxies = get_proxies(group_proxy_th)
                while len(proxies) == 0:
                    time.sleep(1)
                    proxies = get_proxies(group_proxy_th)
                proxy_th = 0
            driver.close()
            driver = create_driver(proxies[proxy_th])

        start_time = time.time()
        data, num_results, flag = search(driver, cp_name, cp_id, cp_key, country)
        end_time = time.time()
        if flag == False:
            driver.close()
            driver = create_driver(proxies[proxy_th])
            count_block += 1
            continue

        if num_results != 0 : #Co ket qua -> dump file
            file_name = './data_website/'+ country +'/'+ str(i)+'_'+cp_id.replace('/','-')+'.json'
            json.dump(data, open(file_name,'w'))
            count_block = 0
            # print('end =', end,'begin =', i, 'country =', sys.argv[1].split('.csv')[0].split('_')[-1], \
            # 'results =', num_results, 'time =', round(end_time-start_time,2), \
            # 'remainder =', end-i)
        else:
            count_block += 1
            if count_block > 5000:
                print('--------------BLOCK :)-------------\n--------------BLOCK :)-------------')
                break
    driver.close()

if __name__ == '__main__':
    main()
