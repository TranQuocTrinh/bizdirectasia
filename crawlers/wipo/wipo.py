import re
import csv
import time
import random
import base64
import requests
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sys

year_max = 2019
year_min = 1949
flag = False # False: write file json, True: call API post data

class Wipo:
    def __init__(self, country):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome("./deps/chromedriver", chrome_options = chrome_options)
        self.driver.get('http://www.wipo.int/branddb/en')
        self.country = country

    def wait(self, min, max):
        start_time = time.time()
        while time.time() < start_time + random.uniform(min,max):
            continue

    def search_company(self, nice_cl, year):
        # search country
        while True:
            try:
                self.driver.find_element_by_css_selector('#ui-id-6 > span').click()
                break
            except:
                continue
        while True:
            try:
                self.driver.find_element_by_css_selector('#OO_input').send_keys(self.country)
                break
            except:
                continue
        # search nice class
        self.driver.find_element_by_css_selector('#ui-id-5 > span').click()
        self.driver.find_element_by_css_selector('#GOODS_CLASS_input').send_keys(str(nice_cl))

        year_keys = {} 
        for i in range(year_min,year_max):
            if i == year_min:
                year_keys[i] = "1823-01-01 TO 1950-01-01"
            else:
                year_keys[i] = str(i)+"-01-01 TO "+str(i+1)+"-01-01"

        # search year
        while True:
            try:
                self.driver.find_element_by_css_selector('#ui-id-4').click()
                break
            except:
                continue
        while True:
            try:
                self.driver.find_element_by_css_selector('#AD_input').send_keys(year_keys[year]+"\n")
                break
            except:
                continue

        # return so trang
        self.wait(1,2)
        try:
            soup = BeautifulSoup(self.driver.page_source, 'lxml').find_all('div',class_="noMatches")[0].get_text()
        except:
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
        if soup == "No documents match your query":
            return False
        else:
            page = soup.find_all("div", class_="skipWindow")[0].get_text()
            page = int(re.sub('[^0-9]','', page))
            return page

    def get_page(self, soup):
        cookies_dict = {}
        for cookie in self.driver.get_cookies():
            cookies_dict[cookie['name']] = cookie['value']
        
        headers = {
        'Accept':'image/webp,image/apng,image/*,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'en-US,en;q=0.9',
        'Connection':'keep-alive',
        'Host':'www.wipo.int',
        'Referer':'http://www.wipo.int/branddb/en/',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
        (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
        }
        data = []
        soup = soup.find_all('tbody')[3]
        for j in range(0, len(soup)-1):
            row = {}
            link = soup.find_all('tr', id=str(j))[0]
            item = link.find_all('td',{'aria-describedby':'gridForsearch_pane_BRAND'})[0]
            
            row["brand"]= item.get_text().strip("\n")
            item = link.find_all('td',{'aria-describedby':'gridForsearch_pane_SOURCE'})[0]
            
            row["source"]= item.get_text()
            item = link.find_all('td',{'aria-describedby':'gridForsearch_pane_STATUS'})[0]
            row["status"]= item.get_text()
            
            item = link.find_all('td',{'aria-describedby':'gridForsearch_pane_score'})[0]
            row["relevance"]= item.get_text()
            
            item = link.find_all('td',{'aria-describedby':'gridForsearch_pane_OO'})[0]
            row["origin"]= item.get_text()
            
            item = link.find_all('td',{'aria-describedby':'gridForsearch_pane_HOL'})[0]
            row["holder"]= item.get_text()
            
            item = link.find_all('td',{'aria-describedby':'gridForsearch_pane_ID'})[0]
            row["number"]= item.get_text()
            
            item = link.find_all('td',{'aria-describedby':'gridForsearch_pane_AD'})[0]
            row["app.date"]= item.get_text()
            
            item = link.find_all('td',{'aria-describedby':'gridForsearch_pane_LOGO'})[0]
            row["image_class"]=""

            item = link.find_all('td',{'aria-describedby':'gridForsearch_pane_NC'})[0]
            row["nice_cl"]= item.get_text()
            
            item = link.find_all('td',{'aria-describedby':'gridForsearch_pane_IMG'})[0]
            img = item.find_all('img')
            if len(img) == 0:
                img = ''
                row["image"] = ""
            else:
                img = img[0]
                image_url = 'http://www.wipo.int/branddb' + img.get('src').strip('.')
                response = requests.get(image_url, headers=headers, cookies=cookies_dict)
                s = base64.b64encode(response.content)
                row["image"] = str(s)
            data.append(row)
        return data

    def get(self, number_pages, nice_cl, year):
        i = 0
        while i <= number_pages:
            try:

                #wait
                self.wait(1,2)
                soup = BeautifulSoup(self.driver.page_source, 'lxml')
                self.wait(1,2)
                start_time = time.time()
                data = self.get_page(soup)
                self.API_post(data, i+1, nice_cl, year, flag) # flag == False, write json ./data/page
                #-----------------------------------------------
                #-  Call API POST data                         -
                #-----------------------------------------------

                print("time craw page",i+1,":", time.time()-start_time)
                if i+1 == number_pages:
                    break
                i += 1
                while True:
                    try:
                        self.driver.find_element_by_css_selector('#results > div.results_navigation.bottom_results_navigation.displayButtons > div.results_pager.ui-widget-content > div.arrow_container > a:nth-child(4)').click() #next page
                        break
                    except:
                        continue
            except:
                continue
        self.driver.find_element_by_css_selector('#search_pane > form > div.search > div > div.search_left.ui-resizable > div.search_container.search_container_left.hasStatus > div.currentSearch > div.searchFunctions > a > span.ui-button-icon-secondary.ui-icon.ui-icon-trash').click() #delete keyword

    def API_post(self, data, page, nice_cl,year, isWriteFile=True):
        countrys = {"VN":"vietnam","TH": "thailand","LA":"laos","KH":"cambodia",
                "ID":"indonesia","MY":"malaysia","SG":"singapore","BN":"Brunei"}

        url = "http://akita.bizdirectasia.com:7777/website/store"

        headers = {"Content-Type":"application/json",
                   "Authorization":"Bearer a4227481879ade148759e3b6f9647619",
                   "cache-control":"no-cache"
                    }
        body = {
                "domain": "http://www.wipo.int",
                "url": "/branddb/en",
                "sector": "",
                "attr": {
                    "size": 30
                    }
                }
        body["parrent"] = countrys[self.country]
        body["label"] = "wipo-"+self.country.lower()+"-"+str(year)+"-"+str(nice_cl)+"-"+str(page)
        body["attr"]["page"] = page
        body["attr"]["year"] = year
        body["attr"]["nicle_cl"] = nice_cl
        body["data"] = data
        if isWriteFile == False:
            json.dump(body, open("./"+countrys[self.country]+"/"+body["label"]+".json", "w"))
        else:
            req = requests.post(url, headers=headers, data=json.dumps(body)).json()
            #return req["status"]


    def craw(self, nice_cl=0, year=year_min):
        #wait 
        self.wait(0.5,1)
        nice_cls = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,53,56,58,70,74,75,80,81,82,90,99,100]
        for cl in nice_cls:
            if cl < nice_cl:
                continue
            elif cl == nice_cl:
                for y in range(year,year_max):
                    start_time = time.time()
                    number_page = self.search_company(cl,y)
                    if number_page == False:
                        print("nicl_cl:",cl,"\tyear:",y,"\tnumber_page:", 0)
                        self.driver.find_element_by_css_selector('#search_pane > form > div.search > div > div.search_left.ui-resizable > div.search_container.search_container_left.hasStatus > div.currentSearch > div.searchFunctions > a > span.ui-button-icon-secondary.ui-icon.ui-icon-trash').click()
                    else:
                        self.get(number_page, cl, y)
                        print("nicl_cl:",cl,"\tyear:",y,"\tnumber_page:", number_page, "\ttime: ", time.time() - start_time)
            else:
                for y in range(year_min,year_max):
                    start_time = time.time()
                    number_page = self.search_company(cl,y)
                    if number_page == False:
                        print("nicl_cl:",cl,"\tyear:",y,"\tnumber_page:", 0)
                        self.driver.find_element_by_css_selector('#search_pane > form > div.search > div > div.search_left.ui-resizable > div.search_container.search_container_left.hasStatus > div.currentSearch > div.searchFunctions > a > span.ui-button-icon-secondary.ui-icon.ui-icon-trash').click()
                    else:
                        self.get(number_page, cl, y)
                        print("nicl_cl:",cl,"\tyear:",y,"\tnumber_page:", number_page, "\ttime: ", time.time() - start_time)
        self.driver.close()


def API_get_name(self, skip, limit=1):
    url = "http://akita.bizdirectasia.com:6868/api/company/identities/thailand"
    headers = {
        "Authorization": "Bearer a4227481879ade148759e3b6f9647619",
        "Content-Type": "application/json"
        }
    body = {}
    body["limit"] = limit
    body["skip"] = skip
    
    req = requests.post(url, headers=headers, data=json.dumps(body)).json()
    name_company = req["items"]["name"]
    return name_company, req["total"]

def main():
    #countrys = ["TH","VN","LA","KH","ID","MY","SG","BN"] #fail Myanmar
    if len(sys.argv) == 1:
        wipo = Wipo("TH")
        wipo.craw()
    if len(sys.argv) == 3:
        wipo = Wipo("TH")
        nice_cl = int(sys.argv[1])
        year = int(sys.argv[2])
        wipo.craw(nice_cl, year)


if __name__ == '__main__':
    main()
