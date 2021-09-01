import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options
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

x = 0
mycountry = sys.argv[1]

class DuckDuckGo:
    def __init__(self,url,address="1"):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")


        self.oneclick = 0
        if address == "1":
            options = Options()
            options.add_argument('--headless')
            self.driver = webdriver.Firefox(options=options)
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
            self.driver = webdriver.Firefox(desired_capabilities=capabilities)#chrome_options = chrome_options,
        self.driver.get(url)
        time.sleep(5)

    def search(self, country, cpyright,congty, flag):
        time.sleep(2)
        tail = {
                "vietnam": '".com.vn"',
                "thailand": '".com.th"',
                "singapore": '".com.sg"',
                "philippines": '".com.ph"',
                "indonesia": '".com.id"',
                "malaysia": '".com.my"',
                "brunei": '".com.bn"',
                "cambodia": '".com.kh"',
                "laos": '".com.la"',
                "myanmar": '".com.mn"'
                }
        css_selector = "#search_form_input"
        if x == 0:
            css_selector = "#search_form_input_homepage"
        search = tail[country.lower()] + " " + cpyright +" "+ congty
        print(search)
        self.driver.find_element_by_css_selector(css_selector).clear()
        self.driver.find_element_by_css_selector(css_selector).send_keys(search)
        self.driver.find_element_by_css_selector(css_selector).send_keys(Keys.ENTER)

        time.sleep(2)
        if flag != "" and self.oneclick==0:
            self.driver.find_element_by_css_selector("#links_wrapper > div.results--main > div.search-filters-wrap > div > div.dropdown.dropdown--region.is-active.has-inactive-region > a").click()
            time.sleep(3)            
            self.driver.find_element_by_css_selector("body > div.site-wrapper.js-site-wrapper > div.modal.modal--dropdown.modal--popout.modal--dropdown--region.has-header.js-dropdown-popout.is-showing > div.modal__wrap > div > div.modal__header > input").send_keys(flag+"\n")
            time.sleep(3)
            self.oneclick = 1
        data = {"search":search}
        data["results"] = self.get_info()
        return data

    def get_info(self):
        soup = BeautifulSoup(self.driver.page_source,'lxml')
        divs = soup.find_all("div", class_="result results_links_deep highlight_d result--url-above-snippet")
        data = []
        for div in divs:
            title = div.find_all("h2")[0].find_all("a")[0].get_text()
            url = div.find_all("span", class_="result__url__domain")[0].get_text()
            data.append({"title":title, "url":url})
            #print(title, "\t", url)
        return data
        

    def next_page(self):
        try:
            self.driver.find_element_by_link_text("Next").click()
            return True
        except:
            return False


def remove_value(lst, value):
    a = []
    for x in lst:
        if x != value:
            a.append(x)
    return a

def read_csv(path):
    data = pd.read_csv(path)
    country, cpyright, congty, flag = list(data["country"]), list(data["copyright"]), list(data["congty"]), list(data["flag"])
    for i,f in enumerate(flag):
        if isinstance(f, float):
            flag[i] = ""
    if mycountry == "vietnam":
        a, b = 0, 5
    elif mycountry == "malaysia":
        a, b = 5, 9
    elif mycountry == "singapore":
        a, b = 9, 13
    elif mycountry == "cambodia":
        a, b = 13, 17
    elif mycountry == "myanmar":
        a, b = 17, 21
    elif mycountry == "philippines":
        a, b = 21, 28
    elif mycountry == "thailand":
        a, b = 28, 34
    elif mycountry == "laos":
        a, b = 34, 36
    elif mycountry == "brunei":
        a, b = 36, 40
    elif mycountry == "indonesia":
        a, b = 40, 45
    print(a, b)
    country = country[a:b]
    cpyright = cpyright[a:b]
    congty = congty[a:b]
    flag = flag[a:b]
    return country, cpyright, congty, flag

address = ["165.22.53.159:3128"]

link = "https://duckduckgo.com"
spider = DuckDuckGo(link)
country, cpyright, congty, flag = read_csv("searchcompanywebsiteforTrinh.csv")

print(country, cpyright, congty, flag)
if len(sys.argv) == 3:
    keycontine = sys.argv[2]   
    flag_word = False
else:
    flag_word = True

for i in range(len(country)):
    print(i, end=" ")
    asci = [chr(i) for i in range(97,123)] + [chr(i) for i in range(48,58)]
    for a in asci:
        for b in asci:
            for c in asci:
                if a > keycontine[0] or (a==keycontine[0] and b >= keycontine[1]) or (a==keycontine[0] and b==keycontine[1] and c >= keycontine[2]):
                    data = spider.search(country[i], cpyright[i], congty[i]+" "+a+b+c,flag[i])
                    x = 1
                    time.sleep(2)
                    json.dump(data, open("./"+mycountry+"/"+country[i]+"_"+congty[i].replace(" ","_")+"_"+a+b+c+"3dotcom.json","w"))
print("______________END_________________")
time.sleep(10)
spider.driver.close()

