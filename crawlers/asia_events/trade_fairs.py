import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import lxml
import time
import json
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import sys
import os
import requests

class TradeFairs:
    def __init__(self,url,address="1"):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        if address == "1":
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
            self.driver = webdriver.Chrome(desired_capabilities=capabilities)#chrome_options = chrome_options,

        self.driver.get(url)


    def get_info(self, page):
        soup = BeautifulSoup(self.driver.page_source,'lxml')
        table = soup.find_all("ul", class_ = "var_border_bottom var_blocklink")[0]
        lis = table.find_all("li")
        datas = {"page": page, "items": []}
        for i,li in enumerate(lis):
            linktext = li.find_all("p")[0].get_text().strip()
            #####
            time.sleep(2)
            print(linktext)
            self.driver.find_element_by_css_selector("#Xi_jm_form_fair_search_industry > div.elem_text_list > ul > li:nth-child("+str(i+1)+")").click()
            time.sleep(2)

            # get detail
            data = self.get_detail()
            data["title"] = linktext
            # json.dump(data, open("sample.json","w"))
            print("item =", i)
            # if chua co thi append
            # nguoc lai thi pass
            datas["items"].append(data)
            # back
            self.driver.execute_script("window.history.go(-1)")
        return datas

    def get_detail(self):
        data = {}
        soup = BeautifulSoup(self.driver.page_source, "lxml")
        table = soup.find_all("table", class_="var_base_color elem_table_basic")[0].find_all("tbody")[0].find_all("tr")
        for tr in table:
            key = tr.find_all("th")[0].get_text().strip().strip("\n").replace("  ","")#.replace("\n","")
            value = tr.find_all("td")[0].get_text().strip().strip("\n").replace("  ","")#.replace("\n","")
            # print(key, "\t", value)
            data[key] = value
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
def crawl_events():

    datas = []
    for page in range(8):
        link = "https://www.jetro.go.jp/en/database/j-messe/country/asia/?dnumber=100&sort=0&_page="+str(page+1)
        spider = TradeFairs(link)
        data = spider.get_info(page)
        name_json = "./data_trade/"+str(page+1)+"__"+".json"
        json.dump(data, open(name_json,"w"))
        datas.append(data)
        print("page =", page)
        spider.driver.close()

# create folder
# if not os.path.exists(folder):
#     os.makedirs(folder)

