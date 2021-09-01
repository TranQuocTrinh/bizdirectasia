import json
import requests
import pandas as pd
import sys

data_folder = "./data"
api_key = "a35d73918332ee2a526aa4e0cf57d581630f06e8"


def read_csv(pathFile):
    df = pd.read_csv(pathFile)
    personal_work_ids = list(df["personal_work_id"])
    people_keys = list(df["people_key"])
    company_keys = list(df["company_key"])
    domains = list(df["domain"])
    first_names = list(df["first_name"])
    last_names = list(df["last_name"])
    return personal_work_ids, people_keys, company_keys, domains, first_names, last_names


def write_csv(pathFile):
    pass

def get_API(domain, first_name, last_name):
    http = "https://api.hunter.io/v2/email-finder?domain="+str(domain)+"&first_name="+str(first_name)+"&last_name=" + str(last_name)+ "&api_key="+api_key

    req = requests.get(http)
    return req

def check_response(req):
    result = "unknown"
    temp = str(req)
    temp = int(temp[-5:-2])
    
    if temp == 200:
        result = "200 - OK"
    if temp == 201:
        result = "201 - Created	The request was successful and the resource was created."
    if temp == 204:
        result = "204 - No content	The request was successful and no additional content was sent."
    if temp == 400:
        result = "400 - Bad request	Your request was not valid."
    if temp == 401:
        result = "401 - Unauthorized	No valid API key was provided."
    if temp == 403:
        result = "403 - Forbidden	You have reached the global rate limit (150 requests per second)."
    if temp == 404:
        result = "404 - Not found	The requested resource does not exist."
    if temp == 422:
        result = "422 - Unprocessable entity	Your request is valid but the creation of the resource failed. Check the errors."
    if temp == 429:
        result = "429 - Too many requests	You have reached your usage limit. Upgrade your plan if necessary."
    if temp == 451:
        result = "451 - Unavailable for legal reasons	The person behind the requested resource has asked us directly or indirectly to stop the processing of this resource. For this reason, you shouldn't process this resource yourself in any way."
    if temp >= 500:
        result = "5XX - Server Errors	Something went wrong on Hunter's end."
    return result

def main():
    skip = int(sys.argv[1])
    line = "company_key,results"
    f = open(data_folder+"/results.csv","a+")
    f.write(line+"\n")
    f.close()
    i = 0
    personal_work_ids, people_keys, company_keys, domains, first_names, last_names = read_csv("people_domain_16_cut_off.csv")
    for (personal_work_id, people_key, company_key, domain, first_name, last_name) in zip(personal_work_ids, people_keys, company_keys, domains, first_names, last_names):
        if i < skip:
            i += 1
        else:
            req = get_API(domain, first_name, last_name)
            if check_response(req) == "200 - OK":
                #write json and results
                data = json.loads(req.text)
                json.dump(data,(open(data_folder+"/"+company_key+".json","w")))

            line = company_key+ check_response(req)
            f = open(data_folder+"/results.csv","a+")
            f.write(line+"\n")
            f.close()
            i += 1
            print(check_response(req), "\t", i)
        

if __name__ == "__main__":
    main()
