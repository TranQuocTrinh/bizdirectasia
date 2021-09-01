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

skip = int(sys.argv[1])
path = './data_company/'
countries = ['cambodia','laos','myanmar','thailand','vietnam','indonesia','philippines','malaysia','brunei','singapore']
#for country in countries:
#    if not os.path.exists(path+country):
#        os.makedirs(path+country)

class CocCoc:
    def __init__(self,url,address="1"):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")


        if address == "1":
            options = Options()
            options.add_argument('--headless')
            self.driver = webdriver.Chrome(chrome_options=chrome_options)
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
            self.driver = webdriver.Chrome(desired_capabilities=capabilities)#chrome_options = chrome_options,
        self.driver.get(url)
        time.sleep(5)

    def search(self, company_name, company_id, company_key):
        search = company_name
        css_selector = '#root > div > div > div._3vpl2 > div > div.Fmwbh > div > div.ANhIW.searchform > input'
        self.driver.find_element_by_css_selector(css_selector).clear()
        self.driver.find_element_by_css_selector(css_selector).send_keys(search+'\n')
        time.sleep(2)
        data = {"search":search,"company_id":company_id, "company_key":company_key}
        data["results"] = self.get_detail()
        return data
    
    def get_detail(self):
        soup = BeautifulSoup(self.driver.page_source, 'lxml').find_all('li', class_='_3ImQB')
        results = []
        for x in soup:
            temp = {}
            temp['title'] = x.find_all('span')[0].get_text().strip()
            temp['url'] = x.find_all('p', class_= '_12x_r')[0].find_all('a')[0]['href']
            temp['content'] = x.find_all('span', class_='khNAr')[0].get_text().strip()
            temp['order'] = str(i)
            results.append(temp)
        return results


url = 'https://coccoc.com/search?query=abc'
# ob = CocCoc(url)
# print(json.dumps(ob.search('công ty cổ phần mường thanh'), indent=4, sort_keys=True))

country = 'vietnam'
folder_data = './data_company/data/'
def read_csv(path):
    df = pd.read_csv(path+country+'.csv')
    return list(df['company_id']), list(df['company_key']), list(df['local_name'])

company_id, company_key, company_name = read_csv(path)

ob = CocCoc(url)
for i in tqdm(range(len(company_name))):
    if i >= skip and i <= int(sys.argv[2]):
        try:
            json.dump(ob.search(company_name[i],company_id[i], company_key[i]),open(folder_data+country+'_'+str(i)+'.json','w'))
        except:
            ob.driver.close()
            ob = CocCoc(url)
            json.dump(ob.search(company_name[i],company_id[i], company_key[i]),open(folder_data+country+'_'+str(i)+'.json','w'))


