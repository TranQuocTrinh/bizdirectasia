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
countries = ['cambodia','laos','myanmar','thailand','philippines','malaysia','brunei','singapore'] # vietnam, indonesia
for country in countries:
    if not os.path.exists(path+country):
        os.makedirs(path+country)
country = sys.argv[1]#countries[0]

class SW:
    def __init__(self,url,address="1"):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        if address == "1":
            self.driver = webdriver.Chrome()#chrome_options=chrome_options)
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
        time.sleep(5)

    def search(self, company_name, company_id, company_key):
        search = company_name + ' ' + country
        css_selector = '#yschsp'

        self.driver.find_element_by_css_selector(css_selector).clear()
        self.driver.find_element_by_css_selector(css_selector).send_keys(search+'\n')
        time.sleep(2)
        data = {"search":search,"company_id":str(company_id), "company_key":company_key}
        results = self.get_detail()

        count_break = 0
        while not results:
            self.driver.refresh()
            time.sleep(1.5)
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

url = 'https://search.yahoo.com/search;_ylt=Awr9DtCJVGddKOsAIblDDWVH?p=abc&fr=sfp&iscqry='


folder_data = './data_company/'+country
def read_csv(path):
    df = pd.read_csv(path+country+'.csv')
    return list(df['company_id']), list(df['company_key']), list(df['english_name'])

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

ips = ["1","165.22.53.159:3128"]
ob = SW(url, ips[0])
for i in tqdm(range(len(company_name))):
    if i >= skip and i < end_skip:
        while True:
            try:
                data = ob.search(company_name[i],company_id[i], company_key[i])
                json.dump(data,open(folder_data+'/'+country+'_'+str(i)+'.json','w'))
                if data["results"] == []:
                    check_blocking += 1
                else:
                    check_blocking = 0
                break
            except:
                ob.driver.close()
                ob = SW(url, ips[0])

        if check_blocking >= 10:
            print("CHAN!!!")
            ob.driver.close()
            break

