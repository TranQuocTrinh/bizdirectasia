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
import pandas as pd
import random

stt = 0
number_search = 1000
pathFile = "cam.csv"
pathFolder = "./data_cam"+str(stt)+"/"
pathResult = "./data_cam"+str(stt)+"/results.csv"



df = pd.read_csv(pathFile)
company_keys = list(df["company_key"])
selfcompany_keys = [str(x).lower() for x in company_keys]
company_names = list(df["trade_style_name"])
selfcompany_names = [str(x).lower() for x in company_names]

class LinkedIn:
    def __init__(self,address):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        
        proxy = {'address':address}
        capabilities = dict(DesiredCapabilities.CHROME)
        capabilities['proxy'] = {'proxyType': 'MANUAL',
                                'httpProxy': proxy['address'],
                                'ftpProxy': proxy['address'],
                                'sslProxy': proxy['address'],
                                'noProxy': '',
                                'class': "org.openqa.selenium.Proxy",
                                'autodetect': False}

        self.driver = webdriver.Chrome(desired_capabilities=capabilities,chrome_options = chrome_options)
        self.driver.get("http://recruitmentgeek.com/tools/linkedin/")

    # def API_get(self, skip, limit=1000):
    #     url = "http://akita.bizdirectasia.com:6868/api/company/identities/thailand"
    #     headers = {
    #         "Authorization": "Bearer a4227481879ade148759e3b6f9647619",
    #         "Content-Type": "application/json"
    #         }
    #     body = {}
    #     body["limit"] = limit
    #     body["skip"] = skip
        
    #     req = requests.post(url, headers=headers, data=json.dumps(body)).json()

    #     return req["items"]
    
    def wait(self,min):
        start_time = time.time()
        while time.time() < start_time + min:
            continue


    def page_results(self, soup):
        page = soup.find_all('div', class_ = 'gsc-cursor')
        if len(page) == 0:
            return 0
        else:
            return len(page[0].find_all('div'))


    
    def search(self, company_key, company_name):
        search = "cambodia & intitle:" + '"- '+ company_name+ '"'+'& "linkedin.com/in/"'
        print("search:", search)
        self.driver.find_element_by_css_selector('#gsc-i-id1').send_keys(search+"\n")
        s = time.time()
        while time.time()-s < 1:
            continue

        page_current = 1
        soup = BeautifulSoup(self.driver.page_source,'lxml')
        try:
            pages = soup.find_all("div", class_="gsc-cursor-page")
        except:
            pages = []
        if len(pages) == 0:
            # get data
            divs = soup.find_all('div')
            if divs[36].get_text() == "No Results":
                return False
            else:
                data = {}
                lst = []
                print("==================================================================")
                divs = soup.find_all("div", class_="gs-webResult gs-result")
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
                            try:
                                image = div.find_all("table", class_="gsc-table-result")[0].find_all('img')[0]
                                print("src =", image['src'])
                                value["image"] = image['src']
                            except:
                                pass
                            lst.append(value)
                            print("------------------------------------------------------------------")
                    except:
                        pass
                print("==================================================================")
                data["company_key"] = company_key
                data["company_name"] = company_name
                data["results"] = lst
                return data
        else:
            data = {}
            lst = []
            page_next = int(pages[len(pages)-1].get_text())
            while page_current < page_next:
                print(page_current, page_next)
                # get data
                divs = soup.find_all('div')
                if divs[36].get_text() == "No Results":
                    return False
                else:
                    print("==================================================================")
                    divs = soup.find_all("div", class_="gs-webResult gs-result")
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
                                try:
                                    image = div.find_all("table", class_="gsc-table-result")[0].find_all('img')[0]
                                    print("src =", image['src'])
                                    value["image"] = image['src']
                                except:
                                    pass
                                lst.append(value)
                                print("------------------------------------------------------------------")
                        except:
                            pass
                    print("==================================================================")
                    data["company_key"] = company_key
                    data["company_name"] = company_name
                    data["results"] = lst
                    try:
                        self.driver.find_element_by_xpath('//*[@id="___gcse_0"]/div/div/div/div[5]/div[2]/div/div/div[2]/div[11]/div/div['+str(page_current+1)+"]").click()
                        self.wait(1)
                    except:
                        break
                    soup = BeautifulSoup(self.driver.page_source,'lxml')
                    try:
                        pages = soup.find_all("div", class_="gsc-cursor-page")
                        page_next = int(pages[len(pages)-1].get_text())
                    except:
                        pages = []
                    page_current += 1
            return data

def API_get(skip):
    company_keys = []
    company_names = []
    for i in range(number_search):
        if i+skip < len(selfcompany_keys):
            company_keys.append(selfcompany_keys[i+skip])
    for i in range(number_search):
        if i+skip < len(selfcompany_names):
            company_names.append(selfcompany_names[i+skip])
    
    return company_keys, company_names

def get_data(skip):
    if skip == 0:
        f = open(pathResult,"a+")
        line = "json_name,remainder,results,profile"
        f.write(line+"\n")
        f.close()
    
    skip_max = len(selfcompany_keys)
    while skip <= skip_max:
        #get API
        company_keys, company_names = API_get(skip)
        
        d = skip
        datas = []
        results = 0
        profile = 0
        ips = get_ips()
        x = 0
        for (company_key, company_name) in zip(company_keys, company_names):
            x += 1
            if x < 500:
                if x % 100 == 1:
                    if x != 1:
                        link.driver.close()
                    link = LinkedIn(ips[x//100])
                else:
                    pass
            if x >= 500:
                x = 0
                ips = get_ips(0)
            start_time = time.time()
            data = link.search(company_key, company_name)
            if data == False:
                print("skip =",d,"\tNo Results")
            else:
                results += 1
                profile += len(data["results"])
                datas.append(data)
                print("skip =",d, time.time()- start_time)
            link.driver.find_element_by_css_selector('#gsc-i-id1').clear()
            d += 1
        f = open(pathResult,"a+")
        line = str(skip)+"_"+str(skip+number_search-1)+".json" + "," + str(len(selfcompany_keys)/number_search-skip/number_search) + ","+ str(results)+ ","+ str(profile)
        f.write(line+"\n")
        f.close()
        json.dump(datas, open(pathFolder+str(skip)+"_"+str(skip+number_search-1)+".json","w"))
        skip += number_search
    

def get_ips(one=1):
    if one == 0:
        requests.get("https://places.bizdirectasia.com/proxy/renew?group=1")
        time.sleep(600)
    driver = requests.get("https://places.bizdirectasia.com/proxy/list?group=1")
    temp = driver.text.split(",")
    ips = []
    for x in temp:
        x = x.lstrip("[").rstrip("]").strip('"')+":3128"
        ips.append(x)
    return ips

def main():
    if len(sys.argv) == 1:
        skip = 0
    else:
        skip = int(sys.argv[1])
    if skip % number_search != 0:
        print("invalid! Please enter skip again!")
        exit()

    start_time = time.time()
    get_data(skip)
    print("total time:", time.time() - start_time)

if __name__ == "__main__":
    main()
