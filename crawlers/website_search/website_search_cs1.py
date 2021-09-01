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

stt = 1
pathFolder = "./data_website"+str(stt)+"/"
pathResult = pathFolder+"result"+str(stt)+".csv"
number_search = 1000
# connect sample
import mysql.connector

mydb = mysql.connector.connect(
    host="68.183.229.8",
    user="bda",
    passwd="zaq1@Wsx",
    database="bda"
)

def get_company(offset, limit = 1000):
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
            }
        ]

countrys = {"VN":"vietnam","TH": "thailand","LA":"laos","KH":"cambodia",
        "ID":"indonesia","MY":"malaysia","SG":"singapore","BN":"brunei","PH":"philippines","MM":"myanmar"}

skip = int(sys.argv[1])
company_keys, company_names = get_company(offset=skip,limit=number_search)
number_requests = 0
while company_keys:
    #get
    if skip != 0:
        company_keys, company_names = get_company(offset=skip,limit=number_search)
    for (company_key, company_name) in zip(company_keys, company_names):
        time.sleep(1)
        search = "intitle:" + '"' + company_name + '" + "'+ countrys[company_key[:2]] + '"'
        print("search:", search)
        start_time = time.time()
        data = requests.get("https://www.googleapis.com/customsearch/v1?key=" + accounts[int(sys.argv[2])]["API_key"] + "&cx=" + accounts[int(sys.argv[2])]["engine_id"] +"&q=" + search) #siterestrict
        number_requests += 1
        #print(data.text)
        check = str(data)
        i = 0
        while check != "<Response [200]>":
            print("requests :", number_requests)
            
            i += 1
            if i > 5:
                print("DAILY LIMIT EXCEEDED!!!! Waiting for another 20 hours")
                time.sleep(72000)
            time.sleep(5)
            data = requests.get("https://www.googleapis.com/customsearch/v1?key=" + accounts[int(sys.argv[2])]["API_key"] + "&cx=" + accounts[int(sys.argv[2])]["engine_id"] +"&q=" + search)
            number_requests += 1
            check = str(data)
        json.dump(data.text, open(pathFolder + str(company_key) + ".json", "w"))
        print("skip = ", skip , "\tstatus = ok\t", "\ttime = ", time.time() - start_time, "\trequests",number_requests)
        skip += 1
