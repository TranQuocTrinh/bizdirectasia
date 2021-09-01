import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import lxml
import time
import json
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import pandas as pd
import sys
import os
import requests
from selenium.webdriver.common.keys import Keys
from tqdm import tqdm

path = './data_company/'
path_des = './data/'
if not os.path.exists(path_des):
    os.makedirs(path_des)

country = sys.argv[1]
if not os.path.exists(path_des+country):
    os.makedirs(path_des+country)

class SW:
    def __init__(self,url,address="1"):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        if address == "1":
            self.driver = webdriver.Chrome(chrome_options=chrome_options)
            pass
        else:
            print("ip: "+str(address))
            # cach 1
            # options = webdriver.ChromeOptions()
            # options.add_argument('--proxy-server=%s' % address)
            # self.driver = webdriver.Chrome(options=options)
            
            # cach 2
            proxy = {'address':address}
            capabilities = dict(DesiredCapabilities.CHROME)
            capabilities['proxy'] = {'proxyType': 'MANUAL',
                                    'httpProxy': proxy['address'],
                                    'ftpProxy': proxy['address'],
                                    'sslProxy': proxy['address'],
                                    'noProxy': '',
                                    'class': "org.openqa.selenium.Proxy",
                                    'autodetect': False}    
        
            self.driver = webdriver.Chrome(desired_capabilities=capabilities)#, chrome_options=chrome_options)
        self.driver.get(url)
        time.sleep(5)

    def search(self, company_name, company_id, company_key):
        search = 'intitle: ' + '- "'+ company_name + '" site:linkedin.com/in'
        css_selector = '#yschsp'

        self.driver.find_element_by_css_selector(css_selector).clear()
        self.driver.find_element_by_css_selector(css_selector).send_keys(search+'\n')
        time.sleep(2)
        data = {"search":search,"company_id":str(company_id), "company_key":company_key, "company_name":company_name}
        results = self.get_detail()

        count_break = 0
        while not results:
            self.driver.refresh()
            time.sleep(1.5)
            results = self.get_detail()
            count_break += 1
            if count_break >= 2:
                break

        data["results"] = results
        return data
    
    def get_detail(self):
        try:
            soup = BeautifulSoup(self.driver.page_source, 'lxml').find_all('ol', class_='mb-15 reg searchCenterMiddle')[0].find_all('li')
        except:
            return []
        results = []
        for i,x in enumerate(soup):
            temp = {}
            try:
                temp['title'] = x.find_all('h3', class_='title')[0].get_text().strip()
                temp['url'] = x.find_all('a')[0]['href']
                temp['content'] = x.find_all('div', class_='compText aAbs')[0].get_text().strip()
                temp['order'] = str(i)
                results.append(temp)
            except:
                pass
        return results

url = 'https://search.yahoo.com/search;_ylt=Awr9DtCJVGddKOsAIblDDWVH?p=abc&fr=sfp&iscqry='


file_ = path + country
def read_csv(path):
    df = pd.read_csv(path +'data_' + country+'.csv')
    return list(df['company_id']), list(df['company_key']), list(df['trade_style_name'])

company_id, company_key, company_name = read_csv(path)
check_blocking = 0

if len(sys.argv) == 4:
    end_skip = int(sys.argv[2])
    skip = int(sys.argv[3])
elif len(sys.argv) == 3:
    skip = int(sys.argv[2])
    end_skip = len(company_name)
else:
    skip = 0
    end_skip = len(company_name)

import ast
import random

ips = ast.literal_eval(requests.get('http://18.140.47.94/proxy/list?group=').text)
ips = [x+':3128' for x in ips]

dct_ip_block = {}
for x in ips:
    dct_ip_block[x] = 0

def pick_ip():
    ips = ast.literal_eval(requests.get('http://18.140.47.94/proxy/list?group=').text)
    ips = [x+':3128' for x in ips]
    index_ip = int(int(sys.argv[2])/100000-1)
    if dct_ip_block[ips[index_ip]] < 20:
        return ips[index_ip]
    else:
        requests.get('http://18.140.47.94/proxy/renew?group=')
        print('WAITING FOR RENEW PROXIES..........')
        time.sleep(900)
        print('RESTART PROXIES')
        ips = ast.literal_eval(requests.get('http://18.140.47.94/proxy/list?group=').text)
        ips = [x+':3128' for x in ips]
        for x in ips:
            dct_ip_block[x] = 0
        #exit()


ip = pick_ip()
ob = SW(url, ip)
for i in tqdm(range(len(company_name))):
    if i >= skip and i < end_skip:
        while True:
            try:
                if str(company_name[i]) != 'nan':
                    data = ob.search(str(company_name[i]),str(company_id[i]), str(company_key[i]))
                    if data["results"] == []:
                        # check_blocking += 1
                        dct_ip_block[ip] += 1
                    else:
                        json.dump(data,open(path_des+country+'/' + country +'_'+str(i)+'.json','w'))
                        # check_blocking = 0
                        dct_ip_block[ip] = 0
                break
            except:
                ob.driver.close()
                ip = pick_ip()
                ob = SW(url, ip)

#        if check_blocking >= 20:
#            print("CHAN!!!")
#            ob.driver.close()
#            break
