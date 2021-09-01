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
from tqdm import tqdm
from selenium.webdriver.common.keys import Keys

url = 'https://doanhnghiepmoi.vn'
class Spider:
    def __init__(self,url,address='1'):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        if address == '1':
            self.driver = webdriver.Chrome(chrome_options = chrome_options)
        else:
            proxy = {'address':address}
            capabilities = dict(DesiredCapabilities.CHROME)
            capabilities['proxy'] = {'proxyType': 'MANUAL',
                                    'httpProxy': proxy['address'],
                                    'ftpProxy': proxy['address'],
                                    'sslProxy': proxy['address'],
                                    'noProxy': '',
                                    'class': "org.openqa.selenium.Proxy",
                                    'autodetect': False}
            self.driver = webdriver.Chrome(desired_capabilities=capabilities, chrome_options = chrome_options)
        self.driver.get(url)
        time.sleep(5)
    
    def search(self,s):
        time.sleep(1)
        css_selector = '#key-word-search > input[type=text]'
        self.driver.find_element_by_css_selector(css_selector).clear()
        self.driver.find_element_by_css_selector(css_selector).send_keys(s+'\n')
        
        try:
            self.driver.find_element_by_css_selector('body > div.page-wrapper > div > section > div > div > div.col-md-9.col-xs-12 > div.main-content > ul > li:nth-child(1) > h3 > a').click()
        except:
            return {}
        result = self.get_data()

        self.driver.execute_script("window.history.go(-1)")
        self.driver.execute_script("window.history.go(-1)")
        # return result
        return result 
    def get_data(self):
        key = {
                'Mã số thuế:':'registration_tax',
                'Địa chỉ trụ sở:':'founded_address',
                'Chủ sở hữu:':'director_names',
                'Ngày cấp:':'founded_year'
                }
        time.sleep(2)
        soup = BeautifulSoup(self.driver.page_source,'lxml')
        row = soup.find_all('div', class_='company-info')[0].find_all('div', class_='row')
        data = {}
        for k in key.keys():
            data[key[k]] = ''
        for r in row:
            div = r.find_all('div')
            if div[0].get_text(strip=True) in key.keys():
                    data[key[div[0].get_text(strip=True)]] = div[1].get_text(strip=True)
        try: 
            data['founded_year'] = '-'.join(data['founded_year'].split('/')[::-1])+' 00:00:00'
        except:
            pass
        return data

# read_csv
df = pd.read_csv('data_vietnam_registration.csv')
ids= list(df['id'])
registration_tax = list(df['registration_tax'])
local_name = list(df['local_name'])
name = list(df['name'])

director_names = list(df['director_names'])    

founded_year = list(df['founded_year'])    

founded_address = list(df['founded_address'])
founded_address = [str(x).replace(' ','') for x in founded_address]


charter_capital = list(df['charter_capital'])

def check_condition(founded_address, founded_year, director_names):
    temp = founded_address.split(',')
    flag = False
    for t in temp:
        if t == "":
            flag = True
    if founded_address == '' or founded_address =='nan' \
    or founded_year == '' or founded_year == 'nan' \
    or director_names == '' or director_names == 'nan' \
    or flag:
        return False
    return True

index_run = []
index_ok = []
for i in range(len(ids)):
    if check_condition(founded_address[i], founded_year[i], director_names[i]) == False:
        index_run.append(i)
    else:
        index_ok.append(i)

#df_run = df.iloc[index_run,:]
#df_run.to_csv('run.csv', index=False)
#df_ok = df.iloc[index_ok,:]
#df_ok.to_csv('ok.csv', index=False)

sp = Spider(url)
print(len(index_run))

a = int(sys.argv[2])
b = int(sys.argv[1])

for i in tqdm(range(len(index_run))):
    if i >= a and i <= b:
        while True:
            try:
                #print(df.iloc[index_run[i]])
                if str(registration_tax[index_run[i]]).lower() == 'nan':
                    #print(local_name[index_run[i]])
                    data = sp.search(local_name[index_run[i]].lower().replace('cty', 'cong ty'))
                else:
                    data = sp.search(str(registration_tax[index_run[i]]))
                if bool(data): #not emptry
                    data['index'] = index_run[i]
                    json.dump(data,open('data/'+str(index_run[i])+'_'+name[index_run[i]].lower().replace(' ','_').replace('/','-')+'.json', 'w'))
                break
            except:
                print('refesh')
                sp.driver.close()
                sp = Spider(url)
sp.driver.close()
#df = pd.DataFrame({'id': ids, '':}
