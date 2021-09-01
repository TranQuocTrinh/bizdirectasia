import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import random
import time
from bs4 import BeautifulSoup
from tqdm import tqdm
import sys
import os
from selenium.webdriver.common.keys import Keys
import random

class SP:

    def __init__(self, url, address='1'):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        #self.driver = webdriver.Chrome(chrome_options=chrome_options)

        if address == '1':
            self.driver = webdriver.Chrome(chrome_options=chrome_options)
        else:
            print("ip: "+str(address))
            # cach 1
            options = webdriver.ChromeOptions()
            options.add_argument('--proxy-server=%s' % address)
            self.driver = webdriver.Chrome()#options=options, chrome_options=chrome_options)

        self.driver.get(url)

    def login(self):
        window_before = self.driver.window_handles[0]
        window_after = self.driver.window_handles[1]
        self.driver.switch_to_window(window_after)
        self.driver.close()

        self.driver.switch_to_window(window_before)
        self.driver.find_element_by_css_selector('body > table > tbody > tr:nth-child(5) > td > table > tbody > tr > td:nth-child(3) > a > img').click()

        window_after = self.driver.window_handles[1]
        self.driver.switch_to_window(window_after)

        self.driver.find_element_by_css_selector('#CHKBOX_0'+str(random.randint(1, 9))).click()
        self.driver.find_element_by_css_selector('body > form > table > tbody > tr:nth-child(4) > td > div > table > tbody > tr:nth-child(19) > td > input:nth-child(2)').click()
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        return soup.find_all('tbody')[1].find('tr').find('td').get_text() == 'Welcome!'

    def search(self, id_):
        self.driver.find_element_by_css_selector('#mi_0_0 > div').click()
        self.driver.find_element_by_css_selector('#mi_0_3').click()
        self.driver.find_element_by_css_selector('#PageContent > table:nth-child(41) > tbody > tr:nth-child(1) > td > form > table > tbody > tr:nth-child(1) > td:nth-child(2) > font > input').send_keys(id_)

        self.driver.find_element_by_css_selector('#PageContent > table:nth-child(41) > tbody > tr:nth-child(1) > td > form > table > tbody > tr:nth-child(3) > td:nth-child(2) > font > input[type=button]:nth-child(1)').click()
    
    def get_info(self):
        data = {}
        soup = BeautifulSoup(self.driver.page_source, 'html.parser').find_all('tbody')

        if soup[2].get_text(strip=True).find('MATCHING RECORD FOUND FOR THE SEARCH INFORMATION INPUT!') == -1:
            tbody = soup[3].find_all('tr')
            for x in tbody:
                tds = x.find_all('td')
                try:
                    data[tds[0].get_text(strip=True).strip(':').lower().replace(' ','_').replace('/','-')] = tds[1].get_text(strip=True)
                except:
                    return False

        return data
import ast
import requests


if not os.path.isdir('data_hongkong/'):
    os.makedirs('data_hongkong/')

url = 'https://www.icris.cr.gov.hk/csci/'
start = int(sys.argv[2])
end = int(sys.argv[1])

def pick_ip(count_ip):
    ips = ast.literal_eval(requests.get('http://18.140.47.94/proxy/list?group=3').text)
    ips = [x+':3128' for x in ips]
    if count_ip < len(ips):
        return ips[count_ip], count_ip + 1
    else:
        requests.get('http://18.140.47.94/proxy/renew?group=3')
        print('Restart proxy')
        time.sleep(360)
        ips = ast.literal_eval(requests.get('http://18.140.47.94/proxy/list?group=3').text)
        ips = [x+':3128' for x in ips]
        return ips[0], 1

ip, count_ip = pick_ip(0)
ob = SP(url, address=ip)
ob.login()
for i in tqdm(range(10000000)):
    if start <= i and i <= end:
        while True:
            while True:
                try:
                    ob.search(str(i))
                    data = ob.get_info()
                    break
                except:
                    time.sleep(60)
                    while True:
                        try:
                            ip, count_ip = pick_ip(count_ip)
                            ob = SP(url, address=ip)
                            ob.login()
                            time.sleep(2)
                            break
                        except:
                            pass

            if data == False:
                print('captcha')
                window_before = ob.driver.window_handles[0]
                window_after = ob.driver.window_handles[1]
                ob.driver.switch_to_window(window_after)
                ob.driver.close()
                ob.driver.switch_to_window(window_before)
                ob.driver.close()

                #time.sleep(60)
                while True:
                    try:
                        ip, count_ip = pick_ip(count_ip)
                        ob = SP(url, address=ip)
                        ob.login()
                        time.sleep(2)
                        break
                    except:
                        pass
            else:
                if data == {}:
                    print('not found')
                    break
                else:
                    #print('dump file')
                    json.dump(data, open('data_hongkong/'+data['cr_no.']+'.json','w'))
                    break
