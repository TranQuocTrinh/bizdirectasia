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

ids = open("remain_ids.txt","r").readlines()
ids = ["0"+x[:-1] for x in ids]
six = set([x[:6] for x in ids])

class Thailand:
    def __init__(self, value):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(chrome_options = chrome_options)
        self.driver.get("http://datawarehouse.dbd.go.th/")
        
        #add cookie
        cookie = {"name" : "JSESSIONID", "domain" : "datawarehouse.dbd.go.th"}
        cookie["value"] = value
        self.driver.add_cookie(cookie)
        self.driver.get("http://datawarehouse.dbd.go.th/index")
        
        time.sleep(10)
        self.driver.find_element_by_css_selector('#lang').click()
        time.sleep(10)

    def wait(self, min, max):
        start_time = time.time()
        while time.time() < start_time + random.uniform(min,max):
            continue

    def API_get_id(self, skip, limit=1000):
        req = []
        for i in range(0,1000):
            req.append(ids[skip+i])
        return req

    def search(self, id_company, time_sleep=5):
        # if len(id_company) != 13:
        #     return -1 # good luck
        try:
            self.driver.find_element_by_css_selector('#textStr').clear()
            self.driver.find_element_by_css_selector('#textStr').send_keys(id_company+"\n")
        except:
            self.driver.find_element_by_css_selector('#textSearch').clear()
            self.driver.find_element_by_css_selector('#textSearch').send_keys(id_company+"\n")    
        
        time.sleep(time_sleep)
        soup = BeautifulSoup(self.driver.page_source,'lxml').find_all('span',id='sTotalElements')[0].get_text()
        if soup == "0":  # no results
            self.driver.find_element_by_css_selector('#textStr').clear()
            return -2
        else:   # yess
            return 0

    def get_info(self):
        data = []
        info = {}

        #lst = ['no.','registered_no.', 'juristic_person_name','registered_type','status','tsic','industry_name', 'province','registered_capital_(baht)','total_revenue_(baht)','net_profit_(loss)(baht)','total_assets_(baht)','shareholders’_equity_(baht)']
        # get table
        soup = BeautifulSoup(self.driver.page_source,'lxml').find_all('table', id='fixTable')[0]
        try:
            trs = soup.find_all('tbody')[0].find_all('tr')
        except:
            pass
        try:
            for j in range(len(trs)):
                # get key 
                ths = soup.find_all('thead')[0].find_all('tr')[0].find_all('th')
                lsttem = [x.get_text().lower() for x in ths]
                lst = []
                for x in lsttem:
                    lst.append(x.replace(' ','_'))
                # get results
                ths = soup.find_all('tbody')[0].find_all('tr')[j].find_all('td')
                results = [x.get_text() for x in ths]

                for (x,y) in zip(lst, results):
                    info[x] = y
                data.append(info)
            return data
        except:
            return False

    def get_data(self, id_company):
        data = {}
        data["tax_number"] = id_company
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
            for id_company in id_companys:
                start_time = time.time()
                print(id_company)
                res = self.search(id_company)
                print(res)
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
        self.driver.close()

    def number_results(self):
        number = BeautifulSoup(self.driver.page_source,'lxml').find_all('span',id='sTotalElements')[0].get_text()
        number = number.replace(",","")
        page = BeautifulSoup(self.driver.page_source,'lxml').find_all('span',id='sTotalPage')[0].get_text()
        page = page.replace(" ","").replace("/","")
        cpage = BeautifulSoup(self.driver.page_source,'lxml').find_all('input',id='cPage')[0]["value"]
        print("number: ", number,"\tpage: ",page, "\tpage_current: ", cpage)

        return int(number), int(page), int(cpage)

def main():

    # skip = int(sys.argv[1])

    # if skip < skip_min(stt) or skip > skip_max(stt):
    #     print("invalid! Please enter skip again! skip in range [",skip_min(stt),",",skip_max(stt),"]")
    #     exit()

    # start_time = time.time()
    # thai = Thailand()
    
    # for (i,id_company) in enumerate(ids):
    #     if skip > i:
    #         continue
    #     res = thai.search(id_company)
    #     if res == 0:
    #         data, line = thai.get_data(id_company)
    #         if data == False:
    #             f = open("./data"+str(stt)+"/results"+str(stt)+".csv","a+")
    #             f.write(str(skip)+","+line+"\n")
    #             f.close()
    #             print("skip = ", skip, "\tid_company: ", id_company, "\terror!!!!!")
    #         elif flag == False:
    #             json.dump(data, open("./data"+str(stt)+"/"+str(skip)+"__"+id_company + ".json", "w"))
    #             f = open("./data"+str(stt)+"/results"+str(stt)+".csv","a+")
    #             f.write(str(skip)+","+line+",ok"+"\n")
    #             f.close()
    #             print("skip = ", skip, "\tid_company: ", id_company, "\ttime: ", time.time() - start_time, "\tremainder: ",skip_max(stt)-skip)
    #         else:
    #             pass
    #     else:
    #         line = str(skip)+","+id_company+","+"search_0"
    #         f = open("./data"+str(stt)+"/results"+str(stt)+".csv","a+")
    #         f.write(line+"\n")
    #         f.close()
    #     skip += 1
    # print("------------------------------------END------------------------------------")
    # print("number of companies:", skip_max(stt)-skip+1, "all time:", time.time()-start_time)

    more_thousand = six
    thai = Thailand(sys.argv[1])
    for (i,id_company) in enumerate(six):
        start_time = time.time()
        res = thai.search(id_company,10)
        
        if res == 0:
            number, page, cpage = thai.number_results()
            row = number/page
            data = thai.get_info()
            if data != False:
                print(data,len(data))
                while page != cpage:
                    #click next page
                    temp = BeautifulSoup(thai.driver.page_source, 'lxml')
                    temp2 = temp
                    while temp2 == temp:
                        thai.driver.find_element_by_css_selector("#next").click()
                        time.sleep(10)
                        temp2 = BeautifulSoup(thai.driver.page_source, 'lxml')

                    number, page, cpage = thai.number_results()
                    data = data + thai.get_info()
                    print(data, len(data))
                json.dump(data,open("./data0/"+str(id_company)+".json"),"w")

        more_thousand.remove(id_company)
        f = open("id_more_thousand.txt","w")
        for x in more_thousand:
            f.write(x+"\n")
        f.close()
        
        line = "skip:" + str(i) +"\tid: " +str(id_company) +"\tnumber_results: " + str(number) + "\ttime:" + str(time.time()-start_time) + "\tremainder: " + str(len(six)-i)
        print(line)
    
if __name__ == '__main__':
    main()
#CMNN 190895361
