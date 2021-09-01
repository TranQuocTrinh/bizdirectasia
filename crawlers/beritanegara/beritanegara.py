import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
from bs4 import BeautifulSoup
import time
import json
import requests
from selenium.webdriver.common.proxy import *
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import sys
import random
from tqdm import tqdm
import os

class Beritanegara:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(chrome_options = chrome_options)


    def get(self,url):
        self.driver.get(url)

    def click(self):
        html = BeautifulSoup(self.driver.page_source, 'lxml')
        soup = html.find_all('div', id='w0')[0].find_all('table', class_='table table-striped table-bordered')[0].find_all('tbody')[0].find_all('tr')
        data = []
        for i in range(len(soup)):
            css_selector = '#w0 > table > tbody > tr:nth-child('+str(i+1)+') > td.text-center > a'
            self.driver.find_element_by_css_selector(css_selector).click()
            #data = get_text()
            time.sleep(2)
            id_ = soup[i]['data-key']
            detail = BeautifulSoup(self.driver.page_source, 'lxml').find_all('div', id='w0')[0].find_all('table', class_='table table-striped table-bordered')[0].find_all('tbody')[0].find('tr', class_='trDetail '+id_).find_all('td')[0].find('table').find('tbody').find_all('td')

            tds = soup[i].find_all('td')
            key1 = ['index','', 'no.bn', 'no.tbn','tahun_terbit','badan_hukum','notaris']
            temp = {}
            for i,x in enumerate(tds):
                if i!= 1:
                    temp[key1[i]] = x.get_text(strip=True)

            key2 = ['tipe_badan_hukum','no_sk','tanggal_sk','no_akta','tanggal_akta','kedudukan']
            for i,x in enumerate(detail):
                temp[key2[i]] = x.get_text(strip=True)

            data.append(temp)
            self.driver.find_element_by_css_selector(css_selector).click()
            time.sleep(1)
        return data

def main():

    if len(sys.argv) == 3:
        begin = int(sys.argv[2])
        end = int(sys.argv[1])

    if len(sys.argv) == 2:
        begin = int(sys.argv[1])
        end = 43222

    sp = Beritanegara()
    for i in tqdm(range(43222)):
        if i >= begin and i <= end:
            x = 0
            while x < 5:
                try:
                    url = 'http://beritanegara.co.id/bntbn/frontend/web/index.php?r=tbl-bnri%2Findex&page='+str(i)
                    sp.get(url)
                    data = sp.click()
                    json.dump(data, open('data/'+str(i)+'.json','w'))
                    break
                except:
                    x += 1

if __name__ == "__main__":
    main()
