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

url = 'http://www.thongtincongty.com'
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
        css_selector = 'body > div.container > div.col-xs-12.col-sm-9 > div:nth-child(2) > form > div > input'
        self.driver.find_element_by_css_selector(css_selector).clear()
        self.driver.find_element_by_css_selector(css_selector).send_keys(s+'\n')
        
        try:
            result = int(BeautifulSoup(self.driver.page_source, 'lxml').find('h4').get_text().split()[1])
            if result > 0:
                self.driver.find_element_by_link_text(s.upper()).click()
            else:
                return {}
        except:
            pass
        # return result
        return self.get_data()

    def get_data(self):
        key = {
                'Mã số thuế':'registration_tax',
                'Địa chỉ':'founded_address',
                'Đại diện pháp luật':'director_names',
                'Ngày cấp giấy phép':'founded_year'
                }
        soup = BeautifulSoup(self.driver.page_source,'lxml')
        temp = soup.find_all('div', class_='jumbotron')[0].get_text().strip('\n').strip().split('   ')
        data = {}
        for k in key.keys():
            data[key[k]] = ''
        for t in temp[1:]:
            if t != '':
                x = t.strip().split(':')
                if x[0] in key.keys():
                    data[key[x[0]]] = x[1].strip()
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
        if registration_tax[index_run[i]] == 'nan':
            data = sp.search(local_name[index_run[i]].lower().replace('cty', 'cong ty'))
        else:
            data = sp.search(str(registration_tax[index_run[i]]))
        if bool(data): #not emptry
            data['index'] = index_run[i]
            json.dump(data,open('data/'+str(index_run[i])+'_'+name[index_run[i]].lower().replace(' ','_')+'.json', 'w'))

sp.driver.close()
#df = pd.DataFrame({'id': ids, '':}
