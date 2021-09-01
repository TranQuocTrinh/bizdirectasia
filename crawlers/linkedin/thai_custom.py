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

stt = 0
number_search = 1000
pathFile = "thai.csv"
pathFolder = "./data_thailand"+str(stt)+"/"
pathResult = "./data_thailand"+str(stt)+"/results.csv"

class LinkedIn:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome()#chrome_options = chrome_options)
        self.driver.get("http://cse.google.com/cse?cx=009679435902400177945:psuoqnxowx8")
        
        df = pd.read_csv(pathFile)
        company_keys = list(df["company_key"])
        self.company_keys = [str(x).lower() for x in company_keys]
        company_names = list(df["trade_style_name"])
        self.company_names = [str(x).lower() for x in company_names]

    def wait(self,min):
        start_time = time.time()
        while time.time() < start_time + min:
            continue

    def API_get(self, skip):
        company_keys = []
        company_names = []
        for i in range(number_search):
            if i+skip < len(self.company_keys):
                company_keys.append(self.company_keys[i+skip])
        for i in range(number_search):
            if i+skip < len(self.company_names):
                company_names.append(self.company_names[i+skip])
        
        return company_keys, company_names
    def page_results(self, soup):
        page = soup.find_all('div', class_ = 'gsc-cursor')
        if len(page) == 0:
            return 0
        else:
            return len(page[0].find_all('div'))

    def search(self, company_key, company_name):
        search = "thailand & intitle:" + '"- '+ company_name+ '"'+'& "linkedin.com/in/"'
        print("search:", search)
        self.driver.find_element_by_css_selector("#gsc-i-id1").send_keys(search+"\n")
        self.wait(1)
        page_current = 1
        soup = BeautifulSoup(self.driver.page_source,'lxml')
        try:
            pages = soup.find_all("div", class_="gsc-cursor-page")
        except:
            pages = []
        if len(pages) == 0:
            # get data
            divs = soup.find_all('div')
            if divs[32].get_text() == "No Results":
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
    
    def get_data(self, skip):
        if skip == 0:
            f = open(pathResult,"a+")
            line = "json_name,remainder,results,profile"
            f.write(line+"\n")
            f.close()

        skip_max = len(self.company_keys)
        while skip <= skip_max:
            #get API
            company_keys, company_names = self.API_get(skip)
            
            d = skip
            datas = []
            results = 0
            profile = 0
            for (company_key, company_name) in zip(company_keys, company_names):
                start_time = time.time()
                data = self.search(company_key, company_name)
                if data == False:
                    print("skip =",d,"\tNo Results")
                else:
                    results += 1
                    profile += len(data["results"])
                    datas.append(data)
                    print("skip =",d, time.time()- start_time)
                self.driver.find_element_by_css_selector('#gsc-i-id1').clear()
                d += 1
            f = open(pathResult,"a+")
            line = str(skip)+"_"+str(skip+number_search-1)+".json" + "," + str(len(self.company_keys)/number_search-skip/number_search) + ","+ str(results)+ ","+ str(profile)
            f.write(line+"\n")
            f.close()
            json.dump(datas, open(pathFolder+str(skip)+"_"+str(skip+number_search-1)+".json","w"))
            skip += number_search
        self.driver.close()

def main():
    if len(sys.argv) == 1:
        skip = 0
    else:
        skip = int(sys.argv[1])
    if skip % number_search != 0:
        print("invalid! Please enter skip again!")
        exit()

    link = LinkedIn()
    start_time = time.time()
    link.get_data(skip)
    print("total time:", time.time() - start_time)

if __name__ == "__main__":
    main()
