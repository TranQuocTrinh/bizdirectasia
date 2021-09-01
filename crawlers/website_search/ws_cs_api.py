import requests
import time
import json
import requests
import pandas as pd
import sys
import datetime

stt = 1
pathFile = "thai.csv"
pathFolder = "./page_2/"
pathResult = "./page_2/results.csv"


API_key = "AIzaSyAGZonb1ATJZ23oxXSaFxtP8pCUO15V1CI"
engine_id = "001069055631844496982:tbminjwmiou"


df = pd.read_csv(pathFile)
company_keys = list(df["company_key"])
selfcompany_keys = [str(x).lower() for x in company_keys]
company_names = list(df["trade_style_name"])
selfcompany_names = [str(x).lower() for x in company_names]

start_skip = int(sys.argv[1])
for (skip,company_name) in enumerate(selfcompany_names):
    if skip < start_skip:
        continue
    search = "thailand & intitle:" + '"- '+ company_name
    #print("search:", search)
    start_time = time.time()
    data = requests.get("https://www.googleapis.com/customsearch/v1/siterestrict?key=" + API_key + "&cx=" + engine_id +"&start=11&q=" + search)
    check = str(data)
    while check != "<Response [200]>":
        time.sleep(15)
        data = requests.get("https://www.googleapis.com/customsearch/v1/siterestrict?key=" + API_key + "&cx=" + engine_id +"&start=11&q=" + search)
        check = str(data)
    json.dump(data.text, open(pathFolder + str(selfcompany_keys[skip]) + "-2.json", "w"))
    print("skip = ", skip , "\tstatus = ok\t","remainder = ", len(selfcompany_keys)-skip , "\ttime = ", time.time() - start_time)#str(datetime.timedelta(seconds=int((len(selfcompany_keys)-skip)*time-time0))))
        #print("skip = ", skip , "\tstatus = error", "\ttime = ", time.time() - start_time)
        #f = open(pathFolder+"results.csv","a+")
        #f.writelines(str(skip) + "," + str(company_keys[skip]) + "," + str(company_name)+"\n")
        #f.close()
        #print(json.dumps(json.loads(data.text), indent=4))
