import requests
import requests.exceptions as reqex
import json
import os
import time
import pandas as pd
from boilerpy3 import extractors, exceptions


def get_html_from_url(website, output_dir="", timeout=10):
    st = time.time()
    # try:
    #     response = requests.get(website, timeout=timeout, stream=False)
    #     print("Time get html success:", time.time() - st)
    #     if response.status_code == 200:
    #         return response.text
    #     else:
    #         return None
    # except requests.exceptions.Timeout as errt:
    #     print("Time get html Timeout:", time.time() - st)
    #     return None
    # except requests.exceptions.RequestException as err:
    #     # print ("OOps: Something Else",err)
    #     print("Time get html RequestException:", time.time() - st)
    #     return None
    # except requests.exceptions.HTTPError as errh:
    #     print("Time get html HTTPError:", time.time() - st)
    #     return None
    # except requests.exceptions.ConnectionError as errc:
    #     print("Time get html ConnectionError:", time.time() - st)
    #     return None
    # else:
    #     print("Time get html else:", time.time() - st)
    #     return None

    try:
        response = requests.get(website, timeout=timeout, stream=False)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except (reqex.Timeout, reqex.ConnectionError, reqex.HTTPError, reqex.RequestException) as err:
        return None
    else:
        return None

def statis_content(cache_dir="cache_cbinsights_content"):
    files = set()
    total = len(pd.read_csv("data_cbinsights.csv"))
    df = []
    while True:
        curr_files = set(os.listdir(cache_dir))
        for f in curr_files:
            if f not in files:
                df.append(json.load(open(os.path.join(cache_dir, f))))
                files.add(f)
        
        os.system("clear")
        res_df = pd.DataFrame(df).fillna("")
        print("Total:", total)
        num_content = len(res_df[res_df["content"] != ""])
        print("Content: {} | Percentage: {:.2f}%".format(num_content, num_content / len(files) * 100))
        num_about_us = len(res_df[res_df["about_us_url"] != ""])
        print("About us url: {} | Percentage: {:.2f}%".format(num_about_us, num_about_us / len(files) * 100))
        num_about_us_content = len(res_df[res_df["about_us_content"] != ""])
        print("About us content: {} | Percentage: {:.2f}%".format(num_about_us_content, num_about_us_content / len(files) * 100))
        print("Files:", len(files))
        time.sleep(1)
        if len(files) == total:
            break

def process_content(content, min_length_paragraph=50, max_length_paragraph=20000):
    content = content.split("\n")
    # remove deduplicate
    new_content = []
    pharse_list = set()
    for p in content:
        if p not in pharse_list:
            pharse_list.add(p)
            new_content.append(p)
    
    content = "\n".join([p for p in new_content if max_length_paragraph > len(p) > min_length_paragraph])
    return content

def get_content_company(website, min_length_paragraph=50, timeout=10):   
    extractor = extractors.KeepEverythingExtractor()
    html = get_html_from_url(website, timeout=timeout)
    try:
        content = extractor.get_content(html) if html is not None and html.strip() != "" else ""
    except exceptions.HTMLExtractionError as err:
        content = ""
    return process_content(content, min_length_paragraph)
