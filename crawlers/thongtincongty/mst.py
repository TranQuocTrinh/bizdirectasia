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

url = 'https://masothue.vn/'
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
    

    def search_mst(self, search):
        self.driver.find_element_by_css_selector("#search").send_keys(search+"\n")
        time.sleep(2)
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        check1 = soup.find_all("div", class_="modal-body")[0].get_text().strip()
        
        if check1 != "":
            self.driver.find_element_by_css_selector("#modal-inform > div > div > div.modal-footer > button").click()
            data = {}
        else:
            try:
                data = self.get_data_mst()
            except:
                temp = BeautifulSoup(self.driver.page_source,'lxml')
                temp1 = temp
                while temp1 == temp:
                    try:
                        self.driver.find_element_by_css_selector("#main > section > div > div.tax-listing > div:nth-child(2) > div > a").click()
                                #main > section > div > div.tax-listing > div:nth-child(2) > h3").click()
                        time.sleep(1)
                        #self.driver.navigate().refresh()
                        temp1 = BeautifulSoup(self.driver.page_source,'lxml')
                    except:
                        pass
                data = self.get_data_mst()
        return data

    def get_data_mst(self):
        soup = BeautifulSoup(self.driver.page_source,'lxml').find_all("tbody")[0].find_all('tr')
        data = {"founded_addresss":"","director_names":"","registration_tax":"","founded_year":"","title":""}
        data["title"] = BeautifulSoup(self.driver.page_source,'lxml').find_all("h1")[0].get_text()
        for tr in soup:
            td = tr.find_all('td')
            try:
                if td[0].get_text().strip() == 'Địa chỉ':
                    data["founded_address"] = td[1].get_text().strip()
                if td[0].get_text().strip() == 'Người đại diện':
                    data["director_names"] = td[1].get_text().strip()
                if td[0].get_text().strip() == 'Mã số thuế':
                    data["registration_tax"] = td[1].get_text().strip()
                if td[0].get_text().strip() == 'Ngày hoạt động':
                    data["founded_year"] = td[1].get_text().strip()
                
                # print(company_name)
                # print("Ma So Thue: ",ma_so_thue)
                # print("Nguoi dai dien: ", nguoi_dai_dien)
                # print("Dia chi: ", address)
                # print("------------------------------------------------")
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

index_run = json.load(open('index_run_remainder.json'))#[]
index_ok = []
#for i in range(len(ids)):
#    if check_condition(founded_address[i], founded_year[i], director_names[i]) == False:
#        index_run.append(i)
#    else:
#        index_ok.append(i)

#df_run = df.iloc[index_run,:]
#df_run.to_csv('run.csv', index=False)
#df_ok = df.iloc[index_ok,:]
#df_ok.to_csv('ok.csv', index=False)
ids =['157.245.206.72:3128','157.245.202.149:3128','157.245.202.148:3128','157.245.198.149:3128','157.245.206.148:3128']

sp = Spider(url,ids[int(sys.argv[3])])
print(len(index_run))
a = int(sys.argv[2])
b = int(sys.argv[1])

for i in tqdm(range(len(index_run))):
    if i >= a and i <= b:
        while True:
            try:
                if str(registration_tax[index_run[i]]).lower() == 'nan':
                    data = sp.search_mst(local_name[index_run[i]].lower().replace('cty', 'cong ty'))
                else:
                    data = sp.search_mst(str(registration_tax[index_run[i]]))
                if bool(data): #not emptry
                    data['index'] = index_run[i]
                    data['company_name'] = local_name[index_run[i]].lower().replace('cty', 'cong ty')
                    #print(data)
                    json.dump(data,open('data/'+str(index_run[i])+'_'+str(name[index_run[i]]).lower().replace(' ','_').replace('/','-')+'.json', 'w'))
                break
            except:
                sp.driver.close()
                sp = Spider(url, ids[int(sys.argv[3])])

sp.driver.close()
#df = pd.DataFrame({'id': ids, '':}
