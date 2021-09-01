import pandas as pd
import json
from bs4 import BeautifulSoup
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import sys
import time
import os
import ast
import requests
import random

if not os.path.exists('./data_website/'):
    os.makedirs('./data_website/')
if not os.path.exists('./data_website/'+sys.argv[1].split('.csv')[0].split('_')[-1]):
    os.makedirs('./data_website/'+sys.argv[1].split('.csv')[0].split('_')[-1])


def pick_proxy(url_get='http://68.183.229.8:9069/proxy/list', url_renew='http://68.183.229.8:9069/proxy/renew'):
    r = requests.get(url_get)
    ips = ast.literal_eval(r.text)
    ips = [ip + ':3128' for ip in ips]

    return random.choice(ips)

IP = pick_proxy()

def create_driver(address=IP, url='http://search.nifty.com/'):
    # set hiden chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # set proxy
    proxy = {'address':address}
    capabilities = dict(DesiredCapabilities.CHROME)
    capabilities['proxy'] = {'proxyType': 'MANUAL',
                            'httpProxy': proxy['address'],
                            'ftpProxy': proxy['address'],
                            'sslProxy': proxy['address'],
                            'noProxy': '',
                            'class': "org.openqa.selenium.Proxy",
                            'autodetect': False} 
    print('IP = {}'.format(address))
    driver = webdriver.PhantomJS(desired_capabilities=capabilities) #Chrome(desired_capabilities=capabilities) #chrome_options=chrome_options,  #
    #driver.set_window_size(0,0)
    driver.get(url)
    time.sleep(10)
    return driver

def extract_detail(soup):
    try:
        soup.find('ul', id='websrchul').findAll('li')
    except:
        return []

    data = []
    i = 0
    for x in soup.find('ul', id='websrchul').findAll('li'):
        try:
            temp = {}
            temp['title'] = x.find('a').find('h3').getText(strip=True)
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
        'taiwan':  'Taiwan',
        'japan': 'Japan',
        'newzealand': 'Newzealand',
        'australia': 'Australia'
    }
    search = company_name + ' ' + countrys[country] + '\n'
    flag_search = False
    for i in range(20):
        try:
            css_selector = '#srchTxt'
            driver.find_element_by_css_selector(css_selector).clear()
            driver.find_element_by_css_selector(css_selector).send_keys(search)
            flag_search = True
            break
        except:
            pass

    if flag_search == False:
        for i in range(20):
            try:
                css_selector = '#srchTxt'
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
    
    df = df[begin:end].reset_index(drop=True)
    #create driver
    driver = create_driver()#'https://search.goo.ne.jp/')

    count_block = 0
    count_requests = 1  # 100 requests/proxy
    for i in tqdm(range(len(df.company_id))):
        try:
            cp_id, cp_key, cp_name = str(df.company_id[i]), str(df.company_key[i]), \
                                        str(df.company_name[i])
        except:
            cp_id, cp_key, cp_name = str(df.company_id[i]), str(df.company_key[i]), \
                                        str(sys.argv[1]).split('.')[-2].split('_')[-1]
        # if i < begin or i > end:    # begin <= i <= end
        #     continue

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
            print('end= {} \t begin= {} \t remainder= {} \t time= {}'.format(end, begin+i, end-i-begin-1,round(end_time-start_time,2)))
        else:
            print('no results')
            count_block += 1
            if count_block > 5000:
                print('--------------BLOCK :)-------------\n--------------BLOCK :)-------------')
                break
    driver.close()

if __name__ == '__main__':
    main()
