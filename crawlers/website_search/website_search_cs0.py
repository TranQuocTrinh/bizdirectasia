import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
from bs4 import BeautifulSoup
import time
import json
import requests
import sys
import pandas as pd
import random

stt = 0
pathFolder = "./data_website"+str(stt)+"/"
pathResult = pathFolder+"result"+str(stt)+".csv"
fileyellowpage = "yellowpage.txt"


number_search = 1000
# connect sample
import mysql.connector

import re
start_time_request = time.time()

def get_company(offset, limit = 1000):
    mydb = mysql.connector.connect(
        host="68.183.229.8",
        user="bda",
        passwd="zaq1@Wsx",
        database="bda"
    )
    company_keys, company_names = [], []
    mycursor = mydb.cursor()
    mycursor.execute("SELECT `index` FROM progress_tracking where `key`='google-search-info' limit 1")
    row = mycursor.fetchone()
    if row != None:
        offset = row[0]
    mycursor.execute(""" select company_key, tradestyle from pending_google_search LIMIT """ + str(offset) + ", "+ str(limit))
    myresult = mycursor.fetchall()
    if len(myresult) > 0:
        for x in myresult:
            companyKey = x[0]
            tradestyle = x[1]
            # search resutll
            offset += 1
        mycursor.execute(""" select company_key, tradestyle from pending_google_search LIMIT """ + str(offset) + ", "+str(limit))
        myresult = mycursor.fetchall()
        company_keys = [x[0] for x in myresult]
        company_names = [x[1] for x in myresult]

    return company_keys, company_names


accounts = [
        {
            "API_key": "AIzaSyAt7or30NhZrIbU0floaPYjXebHBT9ms3s",
            "engine_id": "001069055631844496982:itbwp0abpvo"
            },
        {
            "API_key": "AIzaSyBWMgwraec7PD5FWnj1p8edWZGYBa3prDI",
            "engine_id": "006465022782899725077:zzbppnu6lye"
            },
        {
            "API_key": "AIzaSyCIDeBR4SO3QL-eTiIVP_yTnL8jCnHr8qs",
            "engine_id": "014458517531167187978:jj28nwfen58"
            },
        {
            "API_key": "AIzaSyCSLB86I9PVjsm8--_dFeX77Uj3EJnKXF0",
            "engine_id": "016071571866985734339:7ntq8bnirqo"
            }
        ]

countrys = {"VN":"vietnam","TH": "thailand","LA":"laos","KH":"cambodia",
        "ID":"indonesia","MY":"malaysia","SG":"singapore","BN":"brunei","PH":"philippines","MM":"myanmar"}

dict_link = [{
            "link": "facebook",
            "count": 8
            }]

new_links = open(fileyellowpage,"r").read().strip().split("\n")

def update_dict_link(new_links, index=1):
    for (i,x) in enumerate(dict_link):
        if x["link"] in new_links:
            dict_link[i]["count"] += 1
            new_links.remove(x["link"])
    for x in new_links:
        item = {}
        item["link"] = x
        if index == 0:
            item["count"] = 8
        else:
            item["count"] = 0
        dict_link.append(item)
    remove_link = []
    for x in dict_link:
        if x["count"] > 7 and x["link"] not in remove_link:
            remove_link.append(x["link"])
    return remove_link
remove_link = update_dict_link(new_links,0)

skip = int(sys.argv[1])
company_keys, company_names = get_company(offset=skip,limit=number_search)
number_requests = 0
check_account = [True]*len(accounts)
while company_keys:
    account_current = 0
    #get
    if skip != 0:
        company_keys, company_names = get_company(offset=skip,limit=number_search)
    for (company_key, company_name) in zip(company_keys, company_names):
        start_time = time.time()
        time.sleep(1)
        search ='Copyright © tradestyle + "' + re.sub('[^A-Za-z0-9]+', ' ', company_name).strip() + '" + '+ countrys[company_key.strip()[:2]]
        
        # remove_link = update_dict_link(new_links)
        for link in remove_link:
            search = search + " -"+link

        print("---------------------len(dict_link)", len(dict_link))
        print("search:", search)
        print("yellowpage: ", remove_link)
        data = requests.get("https://www.googleapis.com/customsearch/v1?key=" + accounts[account_current]["API_key"] + "&cx=" + accounts[account_current]["engine_id"] +"&q=" + search) #siterestrict
        number_requests += 1
        #print(data.text)
        check = str(data)
        i = 0
        if check != "<Response [200]>":
            print(data.text)
            print(data)
        while check != "<Response [200]>":
            print("requests :", number_requests)
            i += 1
            if i > 9:
                check_account[account_current] = False
                print("account ", account_current," false!")
                print(check_account)

                if all(item==False for item in check_account):
                    print("DAILY LIMIT EXCEEDED!!!! Waiting for another 5 hours") 
                    print("Time remaining: 1 hours")
                    time.sleep(3600)
                    start_time_request = time.time()
                    check_account = [True, True, True]
                    account_current = 0
                else:
                    acc = 0
                    while check_account[acc] == False:
                        acc += 1
                    account_current = acc
                    i = 0
            data = requests.get("https://www.googleapis.com/customsearch/v1?key=" + accounts[account_current]["API_key"] + "&cx=" + accounts[account_current]["engine_id"] +"&q=" + search)
            number_requests += 1
            check = str(data)
        json.dump(data.text, open(pathFolder + str(company_key.replace("/","_")) + ".json", "w"))
        data_json = json.loads(data.text)
        new_links = []
        try:
            for i in range (0, len(data_json["items"])):
                link = data_json["items"][i]["link"].split("/")[2].split(".")[:-1]
                if link[0] == "www":
                    link = link[1:]
                link = ".".join(link)
                # new_links.append(link)
        except:
            pass # "no results" Google said.

        f = open(fileyellowpage,"w")
        for x in remove_link:
            f.write(x+"\n")
        f.close()
        print("skip = ", skip , "\tstatus = ok\t","\taccount = ",account_current, "\ttime = ", time.time() - start_time, "\trequests",number_requests)
        skip += 1
