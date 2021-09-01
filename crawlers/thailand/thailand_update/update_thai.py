import re
import time
import random
import json
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sys
import urllib.request
from selenium import webdriver
from PIL import Image
from io import BytesIO
import new_recaptcha_coordinates as gc
from selenium.webdriver.common.proxy import *
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# ids = open("remain_ids.txt","r").readlines()
# ids = ["0"+x[:-1] for x in ids]
# six = list(set([x[:6] for x in ids]))

class Thailand:
    def __init__(self, address='1'):
        # hide window
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
        if address == '1':
            self.driver = webdriver.Chrome()#chrome_options = chrome_options)
        else:
            print(address)
            self.driver = webdriver.Chrome()#chrome_options = chrome_options, desired_capabilities=capabilities)

        self.driver.get("http://datawarehouse.dbd.go.th/")        
        css_selector = "body > div.page > div.page-wrapper > div > div.container > div:nth-child(2) > div.panel.panel-link > a > u"
        self.driver.find_element_by_css_selector(css_selector).click()
        time.sleep(3)
        # self.driver.find_element_by_css_selector('#lang').click()

    def screenshot_captcha(self):
        element = self.driver.find_element_by_css_selector("#loginForm > div.input-group.captcha-group > span > img")
        location = element.location
        size = element.size
        png = self.driver.get_screenshot_as_png()
    
        im = Image.open(BytesIO(png))
    
        left = location['x']
        top = location['y']
        right = location['x'] + size['width']
        bottom = location['y'] + size['height']
    
        im = im.crop((left, top, right, bottom)) # defines crop points
        im.save('captcha.png') # saves new cropped image

    def search(self, id_company, first, time_sleep=3):
        self.driver.get('https://datawarehouse.dbd.go.th/fin/profitloss/5/'+id_company)
        soup = BeautifulSoup(self.driver.page_source,'lxml')
        time.sleep(time_sleep)

        try:
            code = int(soup.find_all('div', class_='content')[0].find_all('h5')[0].get_text(strip=True))
        except:
            code = 200

        return code # 500, 401, 200

    def get_info(self,id_company):
        info = {}
        # get table
        soup = BeautifulSoup(self.driver.page_source,'lxml')
        year = soup.find_all('table',id='fixTable')[0].find_all('thead')[0].find_all('th', colspan="2")
        year = [y.get_text(strip=True) for y in year]

        tds = soup.find_all('table',id='fixTable')[0].find_all('tbody')[0].find_all('tr')[1].find_all('td')[1:]
        data = [td.get_text(strip=True) for td in tds]

        info['registration_tax'] = id_company
        info['total_revenue'] = []
        for i,y in enumerate(year):
            temp = {}
            temp['year'] = y
            temp['amount'] = data[2*i]
            temp['%change'] = data[2*i+1]
            info['total_revenue'].append(temp)
        return info

    def number_results(self):
        number = BeautifulSoup(self.driver.page_source,'lxml').find_all('span',id='sTotalElements')[0].get_text()
        number = number.replace(",","")
        page = BeautifulSoup(self.driver.page_source,'lxml').find_all('span',id='sTotalPage')[0].get_text()
        page = page.replace(" ","").replace("/","")
        cpage = BeautifulSoup(self.driver.page_source,'lxml').find_all('input',id='cPage')[0]["value"]
        print("number: ", number,"\tpage: ",page)

        return int(number), int(page), int(cpage)

def remove_value(lst, value):
    lst_temp = []
    for (i,x) in enumerate(lst):
        if x != value:
            lst_temp.append(x)
    return lst_temp

import random

def login():
    address1 = ['178.128.117.159:3128','178.128.125.142:3128',
            '178.128.112.158:3128','178.128.116.118:3128']
    address2 = ['178.128.124.43:3128','178.128.126.65:3128',
            '178.128.121.9:3128','178.128.121.223:3128']


    print('Login...............')
    again = 0
    while again < 4:
        again += 1
        #if sys.argv[3] == '1':
        #    thai = Thailand(address1[random.randint(0,len(address1)-1)])
        #else:
        #    thai = Thailand(address2[random.randint(0,len(address1)-1)])
        thai = Thailand()
        thai.screenshot_captcha()
        capt = gc.get_captcha('captcha.png')
        if capt != "":
            try:
                thai.driver.find_element_by_css_selector("#captchaCode").send_keys(capt+"\n")
                time.sleep(3)
            except:
                pass
            try:
                thai.driver.find_element_by_css_selector("#lang").click() # switch English
                time.sleep(4)
                print('Login success')
                return thai
            except:
                thai.driver.close()
        else:
            thai.driver.close()
            print("HET TIEN.................:((((((((((")
    
    print("Login ERROR!!!")
    exit()

from tqdm import tqdm

def main():

    end = int(sys.argv[1])
    begin = int(sys.argv[2])
    ids = json.load(open("registration_tax.json"))
    ids = ids[begin:end]
    start_time = time.time()
    thai = login()
    count_to_reset = 0

    for i,id_company in enumerate(ids):
        while True:
            try:
                # search and get data
                st = time.time()
                res = thai.search(id_company, count_to_reset)
                time.sleep(1)
                count_to_reset += 1
                if res == 200:
                    data = thai.get_info(id_company)
                    print(data)
                    time.sleep(2)
                    print("\nskip= ", begin+i,"\tid=",id_company, "\tremain=", len(ids)-i, "\ttime= %.2f" % (time.time()-st))
                    json.dump(data, open("./data/"+id_company+".json","w"))
                    break
                elif res == 500:
                    break
                elif res == 401: # login again -> search
                    if count_to_reset < 5:
                        print('login again')
                        thai.driver.close()
                        thai = thai.login()
            except:
                thai.driver.close()
                thai = login()
                count_to_reset = 0
    print("------------------------------------END------------------------------------")

if __name__ == '__main__':
    main()
