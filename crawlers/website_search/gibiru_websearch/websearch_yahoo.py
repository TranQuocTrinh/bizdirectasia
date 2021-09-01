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
path = './data_website/'+sys.argv[1].split('.csv')[0].split('/')[-1].split('_')[1]
if not os.path.exists(path):
    os.makedirs(path)



def pick_proxy():
    ips = []
    for i in range(2):
        url_get_i = 'http://68.183.229.8:9069/proxy/list?group='+str(i+1) 
        url_renew_i = 'http://68.183.229.8:9069/proxy/renew?group='+str(i+1)
        r = requests.get(url_get_i)
        ips_gr = ast.literal_eval(r.text)
        ips = ips + [ip + ':3128' for ip in ips_gr]

    return random.choice(ips)



def create_driver(address=None, url='https://search.yahoo.com/'):
    # set hiden chrome => Just for chromedriver
    # chrome_options = Options()
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--disable-dev-shm-usage")

    # set proxy
    if address != None:
        print('IP = {}'.format(address))
        proxy = {'address':address}
        capabilities = dict(DesiredCapabilities.CHROME)
        capabilities['proxy'] = {'proxyType': 'MANUAL',
                                'httpProxy': proxy['address'],
                                'ftpProxy': proxy['address'],
                                'sslProxy': proxy['address'],
                                'noProxy': '',
                                'class': "org.openqa.selenium.Proxy",
                                'autodetect': False} 
        driver = webdriver.PhantomJS(desired_capabilities=capabilities) 
        # driver = webdriver.Chrome(chrome_options=chrome_options, desired_capabilities=capabilities)
        # driver = webdriver.Chrome(desired_capabilities=capabilities)
    else:
        driver = webdriver.PhantomJS()
        # driver = webdriver.Chrome(chrome_options=chrome_options)
    
    driver.get(url)
    time.sleep(4)
    return driver


def extract_detail(soup):
    try:
        sub_soup = soup.findAll('h3', class_='title ov-h')
    except:
        return []

    data = []
    i = 0
    for x in sub_soup:
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
        'taiwan':  'Taiwan',
        'japan': 'Japan',
        'newzealand': 'Newzealand',
        'australia': 'Australia',
        'brunei': 'Brunei',
        'malaysia': 'Malaysia',
        'singapore': 'Singapore', 
        'philippines': 'Philippines',
        'cambodia': 'Cambodia',
        'laos': 'Laos',
        'myanmar': 'Myanmar',
        'thailand': 'Thailand',
        'vietnam': 'Vietnam'
    }
    search = company_name + ' "contact us" ' + countrys[country] + '\n'
    flag_search = False
    for i in range(20):
        try:
            css_selector = '#yschsp'
            driver.find_element_by_css_selector(css_selector).clear()
            driver.find_element_by_css_selector(css_selector).send_keys(search)
            flag_search = True
            break
        except:
            pass

    if flag_search == False:
        for i in range(20):
            try:
                css_selector = '#yschsp'
                driver.find_element_by_css_selector(css_selector).clear()
                driver.find_element_by_css_selector(css_selector).send_keys(search)
                flag_search = True
                break
            except:
                pass

    if flag_search:
        # time.sleep(0.5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        # results = multi_page()
        results = extract_detail(soup)
        data = {'company_id':company_id, 'company_key': company_key, \
                'company_name': company_name, 'results':results}

        return data, len(results), True
    else:
        return {}, 0, False


def main():
    # IP = pick_proxy()
    IP = None
    """
    sys.argv[1]:    file data
    sys.argv[2]:    number of proxy group
    sys.argv[3]:    end
    sys.argv[4]:    begin
    ##################### python  file_data   number_of_proxy_group   end   begin #####################
    """
    # read_csv
    file_data = sys.argv[1]
    country = file_data.split('/')[-1].split('.csv')[0].split('_')[1]
    df = pd.read_csv(file_data)

    end = int(sys.argv[2])
    begin = int(sys.argv[3])
    
    df = df[begin:end].reset_index(drop=True)
    #create driver
    driver = create_driver(address=IP)#'https://search.goo.ne.jp/')

    count_block = 0
    count_requests = 1  # 100 requests/proxy
    for i in tqdm(range(len(df.company_id))):
        if i % 500 == 499 and IP != None:
            IP = pick_proxy()
            driver.close()
            driver = create_driver(address=IP)
        try:
            cp_id, cp_key, cp_name = str(df.company_id[i]), str(df.company_key[i]), \
                                        str(df.trade_style_name[i])
        except:
            cp_id, cp_key, cp_name = str(df.company_id[i]), str(df.company_key[i]), \
                                        str(df.name[i])
        # if i < begin or i > end:    # begin <= i <= end
        #     continue

        start_time = time.time()
        data, num_results, flag = search(driver, cp_name, cp_id, cp_key, country)
        end_time = time.time()
        if flag == False:
            print('driver is false')
            driver.close()
            driver = create_driver(address=IP)#'https://search.goo.ne.jp/')
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
