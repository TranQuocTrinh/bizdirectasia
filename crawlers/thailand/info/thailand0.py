import re
import time
import random
import json
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sys



stt = 0
flag = False    # False: write json, True: call API post data


def skip_min(stt):
    #skips = [0, 29531, 59062, 88593, 118124, 147655, 177168, 206717, 236248, 265779, 295310, 324841]
    skips = [0, 70875, 141750, 212625, 283500]
    return skips[stt]
    
def skip_max(stt):
    #skips = [29530, 59061, 88592, 118123, 147654, 177167, 206716, 236247, 265778, 295309, 324840, 354376]
    skips = [70874, 141749,212614,283499,354376]
    return skips[stt]

f = open("remain_ids.txt","r")
ids = f.readlines()
ids = ["0"+x[:-1] for x in ids]

class Thailand:
    def __init__(self, value):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(chrome_options = chrome_options)
        self.cookie = value

    def wait(self, min, max):
        start_time = time.time()
        while time.time() < start_time + random.uniform(min,max):
            continue

    def API_get_id(self, skip, limit=1000):
        # url = "http://akita.bizdirectasia.com:6868/api/company/identities/thailand"
        # headers = {
        #     "Authorization": "Bearer a4227481879ade148759e3b6f9647619",
        #     "Content-Type": "application/json"
        #     }
        # body = {}
        # body["limit"] = limit
        # body["skip"] = skip
        
        # req = requests.post(url, headers=headers, data=json.dumps(body)).json()

        # return req["items"]
        req = []
        for i in range(0,1000):
            req.append(ids[skip+i])
        return req

    def search(self, id_company):
        if len(id_company) != 13:
            return -1
        self.driver.find_element_by_css_selector('#input3').clear()
        self.driver.find_element_by_css_selector('#input3').send_keys(id_company+"\n")
        self.wait(0.25,0.25)
        soup = BeautifulSoup(self.driver.page_source,'lxml').find_all('span')[0]
        if soup.get_text() == "สถานะ":
            self.driver.find_element_by_css_selector('body > div.ui-dialog.ui-widget.ui-widget-content.ui-corner-all.ui-draggable.ui-resizable.ui-dialog-buttons > div.ui-dialog-buttonpane.ui-widget-content.ui-helper-clearfix > div > button > span').click()
            self.driver.find_element_by_css_selector('#input3').clear()
            return -2
        else:
            pass
            return 0

    def get_info(self):
        info = {}
        lst = ["rank","corporate_registration_number", "original_registration_number","corporate_name","corporate_status","business_category_code","description","sector","province","area/district","subdistrict","registered_capital(baht)"]
        try:
            soup = BeautifulSoup(self.driver.page_source,'lxml').find_all('tbody')[0].find_all('td')
            for (i,td) in enumerate(soup):
                info[lst[i]] = td.get_text()
        except:
            info = False
        return info
    def get_data(self, id_company):
        data = {}
        #data["tax_number"] = id_company
        data["info"] = {}
        line = id_company
        self.wait(0.25,0.25)
        try:
            info = self.get_info()
            if info == False: 
                line = "no"
            else:
                data["info"] = info
        except:
            line = "no"
        
            #return data
        if line != id_company:
            return False, line
        else:
            return data, line

    

    def craw(self, skip):
        self.driver.implicitly_wait(1000)
            #login
        self.login()
            #get company data from id
        print("skip = [",skip,",",skip_max(stt),"]")
        while skip <= skip_max(stt):
            if skip == skip_min(stt):
                line = "skip,id_company,result"
                f = open("./data"+str(stt)+"/results"+str(stt)+".csv","a+")
                f.write(line+"\n")
                f.close()
            # get id from API
            id_companys = self.API_get_id(skip)
            #id_companys = [x["tax_number"] for x in companys]
            for id_company in id_companys:
                start_time = time.time()
                res = self.search(id_company)
                if res == 0:
                    data, line = self.get_data(id_company)
                    if data == False:
                        f = open("./data"+str(stt)+"/results"+str(stt)+".csv","a+")
                        f.write(str(skip)+","+line+"\n")
                        f.close()
                        print("skip = ", skip, "\tid_company: ", id_company, "\terror!!!!!")
                    elif flag == False:
                        json.dump(data, open("./data"+str(stt)+"/"+str(skip)+"__"+id_company + ".json", "w"))
                        f = open("./data"+str(stt)+"/results"+str(stt)+".csv","a+")
                        f.write(str(skip)+","+line+",ok"+"\n")
                        f.close()
                        print("skip = ", skip, "\tid_company: ", id_company, "\ttime: ", time.time() - start_time, "\tremainder: ",skip_max(stt)-skip)
                    else:
                        pass
                        #----------------------------------
                        #-  CALL API POST DATA            -
                        #----------------------------------
                        # self.API_post_data(data)
                        #print("skip = ", skip, "\tid_company: ", id_company, "\ttime: ", time.time() - start_time, "\tremainder: ", skip_max(stt)-skip)
                elif res == -2:
                    line = str(skip)+","+id_company+","+"search_0"
                    f = open("./data"+str(stt)+"/results"+str(stt)+".csv","a+")
                    f.write(line+"\n")
                    f.close()
                else:
                    line = str(skip)+","+id_company+","+"search_13"
                    f = open("./data"+str(stt)+"/results"+str(stt)+".csv","a+")
                    f.write(line+"\n")
                    f.close()
                skip += 1
                if skip > skip_max(stt):
                    break
        self.wait(2,5)
        self.driver.close()
    def login(self):
        self.driver.get("http://datawarehouse2.dbd.go.th/bdw/home/main.html")
        cookie = {"name" : "JSESSIONID", "domain" : "datawarehouse2.dbd.go.th", "path":"/bdw/", "http":"true"}
        cookie["value"] = self.cookie
        self.driver.add_cookie(cookie)
        self.driver.get("http://datawarehouse2.dbd.go.th/bdw/home/main.html")

        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        login = soup.find_all('cufontext')[4]
        if login.get_text() == "Login":
            print("Please login again")
            exit()
        else:
            #click search
            self.driver.find_element_by_css_selector('#content > div.nav > ul > li > ul > li:nth-child(2) > a > dl > dd').click()

def main():

    if len(sys.argv) == 1:
        print("cookie false!")
        exit()
    if len(sys.argv) == 2:
        skip = skip_min(stt)
        value = sys.argv[1]
    if len(sys.argv) == 3:
        value = sys.argv[1]
        skip = int(sys.argv[2])
        
    if skip < skip_min(stt) or skip > skip_max(stt):
        print("invalid! Please enter skip again! skip in range [",skip_min(stt),",",skip_max(stt),"]")
        exit()

    start_time = time.time()
    thai = Thailand(value)
    thai.craw(skip)
    print("------------------------------------END------------------------------------")
    print("number of companies:", skip_max(stt)-skip+1, "all time:", time.time()-start_time)

    
if __name__ == '__main__':
    main()
