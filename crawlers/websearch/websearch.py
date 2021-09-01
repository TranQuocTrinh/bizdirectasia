import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import pandas as pd
from bs4 import BeautifulSoup
import time
import json
import requests
import sys
import pandas as pd
import random
import re
import os

start_time_request = time.time()
country = sys.argv[1]

class WebSearch:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(chrome_options = chrome_options)
        self.driver.get("https://cse.google.com/cse?cx=009462381166450434430:bcvd94io80w")#"https://cse.google.com/cse?cx=009679435902400177945:qb5l2oulqhg")

    def page_results(self, soup):
        page = soup.find_all('div', class_ = 'gsc-cursor')
        if len(page) == 0:
            return 0
        else:
            return len(page[0].find_all('div'))

    def search(self, company_name, company_id, company_key):
        search = company_name.lower() +' + '+country
        print("search:", search)
        self.driver.find_element_by_css_selector("#gsc-i-id1").clear()
        self.driver.find_element_by_css_selector("#gsc-i-id1").send_keys(str(search)+"\n")
        time.sleep(1)
        # get data
        soup = BeautifulSoup(self.driver.page_source,'lxml') 
        divs = soup.find_all('div')
        data = {"search":search,"company_id":company_id, "company_key":company_key}
        if divs[32].get_text() == "No Results":
            data["results"] = []
            return data
        else:
            lst = []
            print("==================================================================")
            divs = soup.find_all("div", class_="gs-webResult gs-result")
            i = 1
            for div in divs:
                try:
                    if div.get_text()[0] != " ":
                        value = {}
                        title = div.find_all("div", class_="gs-title")[0]
                        print("title =", title.get_text())
                        value["title"] = title.get_text()
                        url = div.find_all("div", class_="gsc-url-top")[0].find_all("div", class_="gs-bidi-start-align gs-visibleUrl gs-visibleUrl-long")[0]
                        print("url =", url.get_text())
                        value["url"] = url.get_text()
                        value["content"] = div.find_all('div', class_='gsc-table-result')[0].get_text().strip()
                        value["order"] = str(i)
                        i += 1
                        lst.append(value)
                        print("------------------------------------------------------------------")
                except:
                    pass
            print("==================================================================")
            data["results"] = lst
            return data

def read_csv(path):
    df = pd.read_csv(path+'.csv')
    return list(df['company_id']), list(df['company_key']), list(df['english_name'])
from tqdm import tqdm

def main():
    path = './data_company/'
    countries = ['cambodia','laos','myanmar','thailand','vietnam','indonesia','philippines','malaysia','brunei','singapore']
    for country in countries:
        if not os.path.exists(path+country):
            os.makedirs(path+country)

    skip = int(sys.argv[2])
    company_id, company_key, company_name = read_csv(path+country)

    link = WebSearch()
    start_time = time.time()
    count_hold = 0
    for i in tqdm(range(0, len(company_name[skip:]))):
        d = link.search(company_name[i+skip], str(company_id[i+skip]), company_key[i+skip])
        if not d["results"]:
            count_hold += 1
        else:
            count_hold = 0
        if count_hold >= 10:
            print("CHAN CHAN CHAN!!!")
            link.driver.close()
            exit()
        json.dump(d, open(path+country+'/'+country+'_'+str(i+skip)+'.json','w'))
        print(str(i+skip)+'/'+str(len(company_key)))
    print("total time:", time.time() - start_time)

if __name__ == "__main__":
    main()
