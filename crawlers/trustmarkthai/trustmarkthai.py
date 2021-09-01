import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import lxml
import time

class spider:
    def __init__(self, page):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(chrome_options = chrome_options)
        self.driver.get("https://www.trustmarkthai.com/index.php/component/dbd/main?layout=search_mark")
        time.sleep(5)
        self.driver.find_element_by_xpath('//*[@id="pagechange"]').click()
        time.sleep(1)
        self.driver.find_element_by_xpath('//*[@id="pagechange"]/option['+str(page)+']').click()
    
    def get_table(self):
        data = []
        soup = BeautifulSoup(self.driver.page_source, "lxml").find_all("tbody")[0]
        trs = soup.find_all("tr")
        for (i,tr) in enumerate(trs):
            try:
                try:
                    self.driver.find_element_by_xpath('//*[@id="body_search"]/tr['+str(i+1)+']/td[4]/a').click()
                    flag = 1
                except:
                    self.driver.find_element_by_xpath('//*[@id="body_search"]/tr['+str(i+1)+']/td[5]/a/img').click()
                    flag = 0

                time.sleep(1)
                ##switch to window on chrome
                window_before = self.driver.window_handles[0]
                window_after = self.driver.window_handles[1]
                self.driver.switch_to_window(window_after)
                # processing
                temp = self.get_big_window(flag)
                self.driver.close()
                self.driver.switch_to_window(window_before)
            except:
                pass
                
            tds = tr.find_all("td")
            temp["order"] = tds[0].get_text().strip()
            temp["website"] = tds[1].get_text().strip()
            # print(temp)
            data.append(temp)
        return data
        

    def get_big_window(self, flag):
        if flag == 1:
            keys = ["operator_name", "owner_name", "name_used_in_commercial_operations", "company_name",
                    "identification_number", "online_store_name", "business_type", "type_of_business", 
                    "contact_location", "address", "telephone", "fax", "email", "date_of_receipt_of_dbd_registered",
                    "dbd_expiration_date_registered", "registered_date", "expire_date"]
        else:
            keys = ["operator_name", "owner_name", "name_used_in_commercial_operations", "company_name",
                    "identification_number", "online_store_name", "business_type", "type_of_business", 
                    "contact_location", "address", "telephone", "fax", "email", "date_of_receipt_of_dbd_registered",
                    "registered_date", "date_of_receiving_dbd_verified", "verified_date", "dbd_expiration_date_verified",
                    "dbd_verified_expire_date"]
        temp = {}
        soup = BeautifulSoup(self.driver.page_source, "lxml")
        trs = soup.find_all("tbody")[0].find_all("tr")
        for (i,tr) in enumerate(trs):
            if flag == 1:
                if i > 2 and i < 20:
                    tds = tr.find_all("td")
                    try:
                        temp[keys[i-3]] = tds[1].get_text().strip()
                    except:
                        temp[keys[i-3]] = ""
                    #print(tds[0].get_text().strip(), ":", tds[1].get_text().strip())
            else:
                if i > 3 and i < 23:
                    tds = tr.find_all("td")
                    temp[keys[i-4]] = tds[1].get_text().strip()
        return temp
    def next_page(self):
        self.driver.find_element_by_id("nextpage").click()

import json
import sys
# page = sys.argv[1]

time.sleep(2)
data = json.load(open("data_all.json"))
page_again =[ 803, 1701, 550, 551, 1576, 2213, 170, 171, 172, 1587, 1719, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 448, 449, 2014, 99, 100, 101, 1380, 2147, 2148, 1001, 1002, 1006, 1007, 2032, 1010, 1011, 1400]
# 787, 788, 1685, 1047, 802,
for i,x in enumerate(page_again):
    sp = spider(x)
    time.sleep(1)
    st_time = time.time()
    data = data + sp.get_table()
    json.dump(data,open("data_all.json","w"))
    # sp.next_page()
    end_time = time.time()
    print("page:", x,"\tpage/total:\t",i,"/",len(page_again)-i,'\ttime: ',end_time-st_time, "\torder: ",data[-1]["order"])
    sp.driver.close()

