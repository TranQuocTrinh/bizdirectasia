import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
from bs4 import BeautifulSoup
import time
import json
import requests
import sys

skip_max = 465897


class LinkedIn:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome("./deps/chromedriver", chrome_options = chrome_options)
        self.driver.get("http://recruitmentgeek.com/tools/linkedin/")

    def API_get(self, skip, limit=1000):
        url = "http://akita.bizdirectasia.com:6868/api/company/identities/thailand"
        headers = {
            "Authorization": "Bearer a4227481879ade148759e3b6f9647619",
            "Content-Type": "application/json"
            }
        body = {}
        body["limit"] = limit
        body["skip"] = skip
        
        req = requests.post(url, headers=headers, data=json.dumps(body)).json()

        return req["items"]
    def search(self, company_key, company_name):
        search = "thailand & intitle:" + '"- '+ company_name+ '"'+'& "linkedin.com/in/"'
        print("search:", search)
        self.driver.find_element_by_css_selector('#gsc-i-id1').send_keys(search+"\n")
        s = time.time()
        while time.time()-s < 1:
                continue
        soup = BeautifulSoup(self.driver.page_source,'lxml')
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
    
    def get_data(self, skip):
        if skip == 0:
            f = open("./data/results.csv","a+")
            line = "json_name, remainder, results"
            f.write(line+"\n")
            f.close()
        while skip <= skip_max:
            #get API
            apis = self.API_get(skip)
            company_names = [x["name"] for x in apis]
            company_keys = [x["key"] for x in apis]
            d = skip
            datas = []
            results = 0
            for (company_key, company_name) in zip(company_keys, company_names):
                
                start_time = time.time()
                data = self.search(company_key, company_name)
                if data == False:
                    print("skip =",d,"\tNo Results")
                else:
                    results += 1
                    datas.append(data)
                    print("skip =",d, time.time()- start_time)
                self.driver.find_element_by_css_selector('#gsc-i-id1').clear()
                d += 1
            f = open("./data/results.csv","a+")
            line = str(skip)+"_"+str(skip+999)+".json" + "," + str(465-skip/1000) + ","+ str(results)
            f.write(line+"\n")
            f.close()
            json.dump(datas, open("./data/"+str(skip)+"_"+str(skip+999)+".json","w"))
            skip += 1000
        self.driver.close()

def main():
    if len(sys.argv) == 1:
        skip = 0
    else:
        skip = int(sys.argv[1])
    if skip % 1000 != 0:
        print("invalid! Please enter skip again!")
        exit()

    link = LinkedIn()
    start_time = time.time()
    link.get_data(skip)
    print("total time:", time.time() - start_time)

if __name__ == "__main__":
    main()
