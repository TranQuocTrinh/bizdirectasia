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
from tqdm import tqdm
import os
import pandas as pd
# ids = open("remain_ids.txt","r").readlines()
# ids = ["0"+x[:-1] for x in ids]
# six = list(set([x[:6] for x in ids]))

if not os.path.exists('data_thai_update'):
    os.makedirs('data_thai_update')

try:
    begin = int(sys.argv[2])
    end = int(sys.argv[1])
except:
    begin = 0
    end = 900000
    
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
            self.driver = webdriver.Chrome(chrome_options = chrome_options)
        else:
            print(address)
            self.driver = webdriver.Chrome(desired_capabilities=capabilities, chrome_options = chrome_options)

        self.driver.get("http://datawarehouse.dbd.go.th/")
        css_selector = "body > div.page > div.page-wrapper > div > div.callcenter > div > a:nth-child(2) > img"
        time.sleep(2)
        self.driver.find_element_by_css_selector(css_selector).click() # switch English
        time.sleep(2)
        # self.driver.find_element_by_css_selector('#lang').click()

    def screenshot_captcha(self):
        element = self.driver.find_element_by_css_selector("#loginForm > div.input-group.captcha-group > span > img")
        location = element.location_once_scrolled_into_view
        size = element.size
        self.driver.save_screenshot('captcha/captcha'+'_'+str(end)+'.png')
    
        im = Image.open('captcha/captcha'+'_'+str(end)+'.png')

        left = location['x']
        top = location['y']
        right = location['x'] + size['width']
        bottom = location['y'] + size['height']
    
        im = im.crop((left, top, right, bottom)) # defines crop points
        im.save('captcha/captcha'+'_'+str(end)+'.png') # saves new cropped image


    def get_info_financial(self, business_id, data={}):
        keys_info = ['company_key', 'company_id', 'business_id', 'company_name', 'status', 'registered_date', 'registered_capital', 
                'last_registered_id', 'address', 'tel', 'fax', 'website', 'e-mail_address', 'directors']#, 'industry_group']
        keys_financial = ['total_revenue_2017', 'total_revenue_2018', 'total_revenue_2019', 'net_profit_loss_2017', 'net_profit_loss_2018', 'net_profit_loss_2019']
        keys_directors = ['bod_1', 'bod_2', 'bod_3']
        
        # infomation
        # url = "https://datawarehouse.dbd.go.th/company/profile/5/" + business_id
        # self.driver.get(url)
        try:
            self.driver.find_element_by_css_selector("#textSearch").clear()
            self.driver.find_element_by_css_selector("#textSearch").send_keys(business_id+"\n")
        except:
            self.driver.find_element_by_css_selector("#textStr").clear()
            self.driver.find_element_by_css_selector("#textStr").send_keys(business_id+"\n")
        
        time.sleep(1)
        self.driver.find_element_by_css_selector("#fixTable > tbody > tr > td:nth-child(2)").click()
        soup_info = BeautifulSoup(self.driver.page_source, 'lxml')
        data['juristic_name'] = soup_info.find('h2', class_="purple").getText(strip=True).replace('Juristic Name : ','')
        trs = [x.getText(strip=True).lower().replace(' ', '_') for x in soup_info.findAll('tr')]
        for i,tr in enumerate(trs):
            for key in keys_info:
                if key != 'address' and tr.find(key) != -1:
                    data[key] = tr.replace(key, '').replace('_',' ').strip()
            if tr == 'address':
                data['address'] = trs[i+1].replace('_',' ').strip()

        divs = [x.getText(strip=True) for x in soup_info.findAll('div', class_='box-info mg-bottom-xs')]
        for div in divs:
            if div.find('Industry group in registered document') != -1:
                data['industry_group_doc'] = div.replace('Industry group in registered document','').lower()
            if div.find('Industry group in the latest financial statement') != -1:
                data['industry_group_last'] = div.replace('Industry group in the latest financial statement','').lower()
        
        for i in range(5):
            data['director_'+str(i+1)] = ''
            data['partner_'+str(i+1)] = ''

        ols = soup_info.findAll('ol')
        for ol in ols:
            table = [x.getText(strip=True) for x in ol.findAll('li')]
            try:
                check_table = ol.find_parent('div').find_parent('div').find('h2').getText(strip=True)
            except:
                continue

            if check_table == 'Board of Directors List':
                print("Board of Directors List")
                for i in range(5):
                    try:
                        data['director_'+str(i+1)] = table[i]
                    except:
                        data['director_'+str(i+1)] = ''
            if check_table == 'Board of Partners List':
                print("Board of Partners List")
                for i in range(5):
                    try:
                        data['partner_'+str(i+1)] = table[i]
                    except:
                        data['partner_'+str(i+1)] = ''

        # financial
        # url = "https://datawarehouse.dbd.go.th/fin/profitloss/5/" + business_id
        url = self.driver.current_url
        url = "https://datawarehouse.dbd.go.th/fin/profitloss/" + url.split('/')[-2] + "/" + business_id
        self.driver.get(url)
        self.driver.execute_script("window.scrollTo(0, 1000);")
        time.sleep(4)
        soup_financial = BeautifulSoup(self.driver.page_source, 'lxml')
        table = soup_financial.find('div', class_='page-content').findAll('tr')

        for tr in table:
            tds = tr.findAll('td')
            if tr.getText(strip=True).find('Total Revenue') != -1:
                data['total_revenue_2017'] = tds[1].getText(strip=True)
                data['total_revenue_2018'] = tds[3].getText(strip=True)
                data['total_revenue_2019'] = tds[5].getText(strip=True)

            if tr.getText(strip=True).find('Net Profit (Loss)') != -1:
                data['net_profit_loss_2017'] = tds[1].getText(strip=True)
                data['net_profit_loss_2018'] = tds[3].getText(strip=True)
                data['net_profit_loss_2019'] = tds[5].getText(strip=True)
        self.driver.execute_script("window.history.go(-1)")
        return data

def remove_value(lst, value):
    lst_temp = []
    for (i,x) in enumerate(lst):
        if x != value:
            lst_temp.append(x)
    return lst_temp

import random

def login():
    #proxies = json.load(open('current_proxies.json'))
    #if len(proxies) == 0:
    #    print('All of proxies are blocked!!!')
    #index_proxy = random.randint(0,len(proxies)-1)
    print('Login...............')
    again = 0
    while again < 5:
        again += 1
        while True:
            try:
                proxies = json.load(open('current_proxies.json'))
                index_proxy = random.randint(0,len(proxies)-1)
                thai = Thailand(proxies[index_proxy])
                break
            except:
                #proxies.pop(index_proxy)
                #json.dump(proxies, open('current_proxies.json','w'))
                print('Website not respone waiting ten minutes')
                time.sleep(60)

        thai.screenshot_captcha()
        capt = gc.get_captcha('captcha/captcha'+'_'+str(end)+'.png')
        if capt != "":
            try:
                thai.driver.find_element_by_css_selector("#captchaCode").send_keys(capt+"\n")
                time.sleep(3)
            except:
                pass
            # check login
            soup = BeautifulSoup(thai.driver.page_source, 'lxml')
            try:
                if soup.find('button', id='signinBtn').getText() == 'Sign in':
                    print('Wrong Captcha!!!!!!!')
                    thai.driver.close()
                #thai.driver.find_element_by_css_selector("#lang") # switch English
            except:
                print('Login success')
                return thai
                
        else:
            thai.driver.close()
            print("HET TIEN.................:((((((((((")
    
    print("Login ERROR!!!")
    exit()



def run():

    count_sleep = 0
    
    business_id_all = json.load(open('remain_id.json'))[begin:end]

    thai = login()
    count_begin = 0
    count = 0
    for i in tqdm(range(len(business_id_all))):
        count += 1
        business_id = business_id_all[i]
        #if count % 9 == 0:
        #    thai.driver.close()
        #    thai = login()

        data = {'business_id': business_id}
        
        rep, flag_data = 0, True
        while rep < 2:
            try:
                data = thai.get_info_financial(business_id, data)
                print('begin = {} end = {}'.format(count_begin+begin, end), data)
                print("\n")
                json.dump(data, open('data_thai_update/'+str(count_begin)+'_'+business_id+'.json', 'w'))
                flag_data = False
                count_sleep = 0
                break
            except:
                rep += 1
                print('Login again!!!!')
                #thai.driver.close()
                del thai
                thai = login()
        if flag_data:
            print('bug, close and refresh window')
            count_sleep += 1
            if count_sleep > 5:
                print('sleep 5 minutes because count_sleep > 5')
                time.sleep(300)
                count_sleep = 0
            #thai.driver.close()
            del thai
            thai = login()

        count_begin += 1


if __name__ == '__main__':
    run()

#'Droid Sans Mono', 'monospace', monospace, 'Droid Sans Fallback'
