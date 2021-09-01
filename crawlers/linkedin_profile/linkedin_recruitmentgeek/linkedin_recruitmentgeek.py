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

driver = webdriver.Chrome()#chrome_options=chrome_options)
driver.get('https://recruitmentgeek.com/tools/linkedin/')

def extract_detail(soup):
    data = []
    for x in soup.find('div', class_='gsc-expansionArea').findAll('div', class_='gsc-webResult gsc-result'):
    #try:
        temp = {}
        temp['title'] = x.find('div', class_='gs-title').getText(strip=True)
        temp['url'] = x.find('a')['href']
        data.append(temp)
    #except:
    #    pass
    #print(data)
    return data

def multi_page():
    results = []
    # next_page
    for i in range(2, 11):
        try:
            results = results + extract_detail(BeautifulSoup(driver.page_source, 'html.parser'))
            driver.find_element_by_css_selector('#yui_3_17_2_1_1581349964349_337 > div > div.gsc-wrapper > div.gsc-resultsbox-visible > div > div > div.gsc-cursor-box.gs-bidi-start-align > div > div:nth-child('+str(i)+')')
            print('next page')
            time.sleep(2)
        except:
            time.sleep(1000)
            break

    #current_url = driver.current_url[:-1]
    #driver2 = webdriver.Chrome(chrome_options=chrome_options)
    #driver2.get(current_url)
    #for i in range(1, 11):
    #   driver2.get(current_url+str(i))
    #   len_temp = len(results)
    #   results = results + extract_detail(BeautifulSoup(driver2.page_source, 'html.parser'))
    #   if len(results) == len_temp:
    #       break
    #driver2.close()

    return results

def search(company_name, company_id, company_key):
    search = '"- ' + company_name.split(' ')[0] +'" site:linkedin.com/in\n'
    try:
        css_selector = '#gsc-i-id1'
        driver.find_element_by_css_selector(css_selector).clear()
        driver.find_element_by_css_selector(css_selector).send_keys(search)
    except:
        css_selector = '#gsc-i-id1'
        driver.find_element_by_css_selector(css_selector).clear()
        driver.find_element_by_css_selector(css_selector).send_keys(search)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    results = multi_page()
    return {'company_id':company_id, 'company_key': company_key, 'company_name': company_name, 'results':results}

df = pd.read_csv(sys.argv[1])
begin = int(sys.argv[2])

for i in range(len(df.company_id)):
    cp_id, cp_key, cp_name, trade_name = str(df.company_id[i]), str(df.company_key[i]), \
            str(df.company_name[i]), str(df.trade_style_name[i])

    if i >= begin and cp_name != 'nan':
        if trade_name == 'nan':
            trade_name = cp_name
        start_time = time.time()
        if i % 150 == 0:
            driver.close()
            driver = webdriver.Chrome()#chrome_options=chrome_options)
            driver.get('https://recruitmentgeek.com/tools/linkedin/')

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
        else:
            print('begin =', i, 'results = 0', 'remainder =', len(df.company_id)-i, \
                    'time =', end_time-start_time, \
                    'search = ' + '"- ' + trade_name +'" site:linkedin.com/in' )
        time.sleep(1)
