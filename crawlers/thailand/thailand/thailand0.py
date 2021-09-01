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
    skips = [0, 29531, 59062, 88593, 118124, 147655, 177168, 206717, 236248, 265779, 295310, 324841]
    return skips[stt]

def skip_max(stt):
    skips = [29530, 59061, 88592, 118123, 147654, 177167, 206716, 236247, 265778, 295309, 324840, 354376]
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
        self.driver.find_element_by_css_selector('#input3').send_keys(id_company+"\n")
        self.wait(1.5,2)
        soup = BeautifulSoup(self.driver.page_source,'lxml').find_all('span')[0]
        if soup.get_text() == "สถานะ":
            self.driver.find_element_by_css_selector('body > div.ui-dialog.ui-widget.ui-widget-content.ui-corner-all.ui-draggable.ui-resizable.ui-dialog-buttons > div.ui-dialog-buttonpane.ui-widget-content.ui-helper-clearfix > div > button > span').click()
            self.driver.find_element_by_css_selector('#input3').clear()
            return -2
        else:
            self.driver.find_element_by_css_selector('#content > div.container > div.box-border > div.one_full > table > tbody > tr:nth-child(2) > td:nth-child(2) > a').click()
            return 0

    def get_data(self, id_company):
        data = {}
        data["tax_number"] = id_company
        data["tabs"] = []
        line = id_company
        self.wait(1.5,2)
        try:
            tab0 = self.get_information()
            if tab0 == False: 
                line = ",table0"
            else:
                data["tabs"].append(tab0)
        except:
            line = ",table0"
        while True:
            try:
                self.driver.find_element_by_css_selector('#content > div.nav > ul > li > ul > li:nth-child(4) > a > dl > dd').click()
                break
            except:
                continue
        self.wait(1.7,2.5)
        try:
            tab1 = self.get_table1()
            data["tabs"].append(tab1)
        except:
            line = line + ",table1"
        while True:
            try:
                self.driver.find_element_by_css_selector('#content > div.container > div > div.box-border > input[type="radio"]:nth-child(8)').click()
                break
            except:
                continue
        
        self.wait(1.5,2)
        try:
            tab2 = self.get_table2()
            data["tabs"].append(tab2)
        except:
            line = line + ",table2"

        while True:
            try:
                self.driver.find_element_by_css_selector('#content > div.container > div > div.box-border > input[type="radio"]:nth-child(10)').click()
                break
            except:
                continue
        self.wait(1.7,2.5)
        try:
            tab3 = self.get_table3()
            data["tabs"].append(tab3)
        except:
            line = line + ",table3"
        self.wait(1.5,2)
            #go main screen
        while True:
            try:
                self.driver.find_element_by_css_selector('#content > div.nav > ul > li > ul > li:nth-child(6) > a > dl > dd').click()
                break
            except:
                continue
            #return data
        if line != id_company:
            return False, line
        else:
            return data, line

    def get_information(self):
        tab = {}
        tab["en_label"] = "company information"
        tab["value"] = {}
        key = {
            0:"company_type",
            1:"date_of_registration",
            2:"company_status",
            3:"registered_capital(baht)",
            14:"paid-up_capital(baht)",
            4:"location",
            5:"business_category(coming_from_recent_financial_statements)",
            6:"purpose(from_recent_financial_statements)",
            7:"year_of_submission_of_financial_statements",
            8:"committee",
            9:"board_of_directors",
            10:"phone",
            11:"fax",
            12:"e-mail_address",
            13:"note"
        }
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        trs = soup.find_all('tr')
        if len(trs) == 14:
            for i in range(0, len(trs)):
                td = trs[i].find_all('td')[0]
                temp = td.get_text().strip('\n').strip('\t')
                if len(temp) == 0 or temp == "\xa0 " or temp == "\xa0":
                    temp = ""
                tab["value"][key[i]] = temp
        elif len(trs) == 15:
            for i in range(0, len(trs)):
                td = trs[i].find_all('td')[0]
                temp = td.get_text().strip('\n').strip('\t')
                if len(temp) == 0 or temp == "\xa0 " or temp == "\xa0":
                    temp = ""
                if i < 4:
                    tab["value"][key[i]] = temp
                if i == 4:
                    tab["value"][14] = temp
                if i > 4:
                    tab["value"][key[i-1]] = temp
        else:
            return False
        return tab
            
    def get_table1(self):
        soup =  BeautifulSoup(self.driver.page_source, 'lxml')
        trs = soup.find_all("tr")
        table = []
        for i in range(0,13):
            row = []
            if i == 0:
                th = trs[i].find_all("th")
                year1 = int(th[1].get_text())-543
                year2 = int(th[2].get_text())-543
                year3 = int(th[3].get_text())-543
            if 1 < i < 13:
                td = trs[i].find_all("td")
                for j in range(0,6):
                    row.append(td[j].get_text())
                table.append(row)
        rows_year1 = []
        rows_year2 = []
        rows_year3 = []

        keys= { 0:"net trade receivables",
                1:"left in stock",
                2:"current assets",
                3:"property, plant and equipment",
                4:"non-current assets",
                5:"total assets",
                6:"total current liabilities",
                7:"non-current liabilities",
                8:"total liabilities",
                9:"shareholders' equity",
                10:"total liabilities and shareholders' equity"
                }
        for key in range(0, 11):
            row = {}
            row["key"] = keys[key]
            row["amount"] = table[key][0]
            row["change"] = table[key][1]
            rows_year1.append(row)
        for key in range(0, 11): 
            row = {}
            row["key"] = keys[key]
            row["amount"] = table[key][2]
            row["change"] = table[key][3]
            rows_year2.append(row)
        for key in range(0, 11):
            row = {}
            row["key"] = keys[key]
            row["amount"] = table[key][4]
            row["change"] = table[key][5]
            rows_year3.append(row)
        
        years = []
        years1 = {}
        years1["year"] = year1
        years1["row"] = rows_year1
        years.append(years1)

        years2 = {}
        years2["year"] = year2
        years2["row"] = rows_year2
        years.append(years2)

        years3 = {}
        years3["year"] = year3
        years3["row"] = rows_year3
        years.append(years3)
        
        tab = {}
        tab["en_label"] = "statements of financial position"
        tab["years"] = years
        return tab

    def get_table2(self):
        soup =  BeautifulSoup(self.driver.page_source, 'lxml')
        trs = soup.find_all("tr")
        table = []
        for i in range(0,12):
            row = []
            if i == 0:
                th = trs[i].find_all("th")
                year1 = int(th[1].get_text())-543
                year2 = int(th[2].get_text())-543
                year3 = int(th[3].get_text())-543
            if 1 < i < 12:
                tds = trs[i].find_all("td")
                for td in tds:
                    row.append(td.get_text())
                table.append(row)    
        rows_year1 = []
        rows_year2 = []
        rows_year3 = []

        keys= {
                0:"main revenue",
                1:"total income",
                2:"selling cost",
                3:"gross profit (loss)",
                4:"cost of sales and services",
                5:"total expenditure",
                6:"interest",
                7:"profit before tax",
                8:"income tax",
                9:"net profit (loss)"
                }
        for key in range(0, 10):
            row = {}
            row["key"] = keys[key]
            row["amount"] = table[key][0]
            row["change"] = table[key][1]
            rows_year1.append(row)
        for key in range(0, 10): 
            row = {}
            row["key"] = keys[key]
            row["amount"] = table[key][2]
            row["change"] = table[key][3]
            rows_year2.append(row)
        for key in range(0, 10):
            row = {}
            row["key"] = keys[key]
            row["amount"] = table[key][4]
            row["change"] = table[key][5]
            rows_year3.append(row)
        
        years = []
        years1 = {}
        years1["year"] = year1
        years1["row"] = rows_year1
        years.append(years1)

        years2 = {}
        years2["year"] = year2
        years2["row"] = rows_year2
        years.append(years2)

        years3 = {}
        years3["year"] = year3
        years3["row"] = rows_year3
        years.append(years3)
        
        tab = {}
        tab["en_label"] = "profit and loss statement"
        tab["years"] = years
        return tab
    
    def get_table3(self):
        soup =  BeautifulSoup(self.driver.page_source, 'lxml')
        tables = {
            "profitability_ratios": [
                {
                    "key": "return on assets (roa) (%)"
                },
	            {
                    "key": "return on equity (roe) (%)"
                },
                {
                    "key": "return on gross profit (%)"
                },
	            {
                    "key": "operating return on total revenue (%)"
                },
                {
                    "key": "return on earnings per total revenue (%)"
                }],
            "performance_ratio": [
                {
                    "key":"total assets turnover (times)"
                },
                {
                    "key": "turnover of receivables (times)"
                },
                {
                    "key": "inventory turnover (times)"
                },
                {
                    "key": "operating expenses to total revenues (%)"
                }],
            "liquidity_indicators": [
                {
                    "key": "working capital ratio (times)"
                }],
            "ratio_of_financial_statements": [
                {
                    "key": "total debt to total assets (times)"
                },
                {
                    "key": "total assets to equity ratio (times)"
                },
                {
                    "key": "total debt to equity ratio (times)"
                },
            ]
        }

        trs = soup.find_all("tr")
        for i in range(0,19):
            if i == 0:
                th = trs[i].find_all("th")
                year1 = int(th[2].get_text())-543
                year2 = int(th[3].get_text())-543
                year3 = int(th[4].get_text())-543
            if 1 < i < 7:
                tds = trs[i].find_all("td")
                for j in range(2, 5):
                    tables["profitability_ratios"][i-2][year1] = tds[j].get_text()
                    tables["profitability_ratios"][i-2][year2] = tds[j].get_text()
                    tables["profitability_ratios"][i-2][year3] = tds[j].get_text()
            if 7 < i < 12:
                tds = trs[i].find_all("td")
                for j in range(2, 5):
                    tables["performance_ratio"][i-8][year1] = tds[j].get_text()
                    tables["performance_ratio"][i-8][year2] = tds[j].get_text()
                    tables["performance_ratio"][i-8][year3] = tds[j].get_text()
            if i == 13:
                tds = trs[i].find_all("td")
                for j in range(2, 5):
                    tables["liquidity_indicators"][i-13][year1] = tds[j].get_text()
                    tables["liquidity_indicators"][i-13][year2] = tds[j].get_text()
                    tables["liquidity_indicators"][i-13][year3] = tds[j].get_text()
            if 14 < i < 18:
                tds = trs[i].find_all("td")
                for j in range(2, 5):
                    tables["ratio_of_financial_statements"][i-15][year1] = tds[j].get_text()
                    tables["ratio_of_financial_statements"][i-15][year2] = tds[j].get_text()
                    tables["ratio_of_financial_statements"][i-15][year3] = tds[j].get_text()
        tab = {}
        tab["en_label"] = "financial ratios"
        tab["tables"] = tables
        return tab

    def craw(self, skip):
        self.driver.implicitly_wait(1000)
            #login
        self.login()
            #get company data from id
        print("skip = [",skip,",",skip_max(stt),"]")
        while skip <= skip_max(stt):
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
