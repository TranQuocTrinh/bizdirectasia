import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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
import random

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
        
            self.driver = webdriver.Chrome(desired_capabilities=capabilities, chrome_options=chrome_options)
        self.driver.get(url)
        time.sleep(3)

    def search(self, company_name, company_id):
        search = company_name
        css_selector = '#yschsp'

        self.driver.find_element_by_css_selector(css_selector).clear()
        self.driver.find_element_by_css_selector(css_selector).send_keys(search.encode('utf-8').decode('utf-8'))
        self.driver.find_element_by_css_selector(css_selector).send_keys('\n')
        #url = 'https://search.yahoo.com/search;_ylt=Awr9DuKfYqFdTQUAoX9DDWVH?p='+search+'&fr=sfp&iscqry='
        #self.driver.get(url)
        time.sleep(1)
        data = {"search":search,"company_id":str(company_id)}
        results = self.get_detail()

        count_break = 0
        while not results:
            self.driver.refresh()
            time.sleep(1.5)
            self.driver.find_element_by_css_selector('body > div > div > div > form > div > button.btn.primary').click()
            results = self.get_detail()
            count_break += 1
            if count_break >= 10:
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

url = 'https://search.yahoo.com/search;_ylt=Awr9DuOLKsFdZ18AQUpDDWVH;_ylc=X1MDMTE5NzgwNDg2NwRfcgMyBGZyAwRncHJpZAM3MTEyLkI5RFQ3T0dYTXJzUGk5VmNBBG5fcnNsdAMwBG5fc3VnZwMxMARvcmlnaW4Dc2VhcmNoLnlhaG9vLmNvbQRwb3MDMARwcXN0cgMEcHFzdHJsAwRxc3RybAMzBHF1ZXJ5A2FiYwR0X3N0bXADMTU3Mjk0MDQzMA--?fr2=sb-top-search&p=abc&fr=sfp&iscqry='
ids = ['165.22.59.95', '165.22.59.147', '165.22.59.105', '165.22.59.99', '165.22.59.96',
        '165.22.59.133', '165.22.59.126', '165.22.59.117', '165.22.59.129', '165.22.59.110']
ids = [x+':3128' for x in ids]
path = './data_company/aus-company_'+sys.argv[1]+'.csv'
def read_csv(path):
    df = pd.read_csv(path)
    return list(df['company_id']), list(df['company_name'])

company_id, company_name = read_csv(path)

if len(sys.argv) == 4:
    end_skip = int(sys.argv[2])
    skip = int(sys.argv[3])
elif len(sys.argv) == 3:
    skip = int(sys.argv[2])
    end_skip = len(company_name)
else:
    skip = 0
    end_skip = len(company_name)
check_blocking = 0

ob = SW(url, ids[random.randint(0,len(ids)-1)])
for i in tqdm(range(len(company_name))):
    if i >= skip and i < end_skip:
        china = 0
        while True:
            try:
                data = ob.search(company_name[i],company_id[i])
                flag = True

            except:
                china += 1
                if china > 2:
                    print('china')
                    break
                ob.driver.close()
                ob = SW(url,ids[random.randint(0,len(ids)-1)])
                flag = False

            if flag:
                json.dump(data,open('./data_websearch/'+'id_'+sys.argv[1]+'_'+str(i)+'.json','w'))
                china = 0
                if data["results"] == []:
                    check_blocking += 1
                else:
                    check_blocking = 0
                break

        if check_blocking >= 10:
            print("CHAN!!!")
            ob.driver.close()
            break
