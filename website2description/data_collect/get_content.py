from bs4 import BeautifulSoup
import requests
import requests.exceptions as reqex
import re
import json
import os
from tqdm import tqdm
import ray
import time
import datetime
import pandas as pd
import sys
import urllib


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

import re
from boilerpy3 import extractors, exceptions

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


def get_about_us_link(website):
    """Extract link of about-us page from company website"""
    template = ["about-us", "about", "aboutus", "about-us", "about-us.html", "about.html", "aboutus.html"]
    response = get_html_from_url(website)
    if response is None:
        return ""
    soup = BeautifulSoup(response, 'html.parser')
    links = soup.find_all('a', href=True)
    for link in links:
        # search about-us link
        if any(re.search(r'about-us', link['href']) for x in template):
            if website in link['href']:
                return link['href']
            elif link['href'][0] and link['href'][0] == "/":
                return website.rstrip("/") + link['href']
    return ""

@ray.remote
def get_content_about_us(website, cache_dir, pba=None):
    """Extract content of about-us page from company website"""
    cache_file = os.path.join(cache_dir, website.replace("/", "_").replace(":", "-") + ".json")
    if os.path.exists(cache_file):
        data = json.load(open(cache_file))
        rep = {
            "website": website,
            "content": data["content"],
            "about_us_url": data["about_us_url"],
            "about_us_content": data["about_us_content"],
        }
    else:
        content = get_content_company(website)
        about_us_link = get_about_us_link(website)
        content_about_us = get_content_company(about_us_link) if about_us_link != "" else ""
        rep = {
            "website": website,
            "content": content,
            "about_us_url": about_us_link,
            "about_us_content": content_about_us,
        }
        json.dump(rep, open(cache_file, "w"))
        
    if pba is not None:
        pba.update.remote(1)
    return rep

def get_content():
    df = pd.read_csv("data_cbinsights.csv")
    cache_dir = "cache_cbinsights_content"
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    if 0:
        start_time = time.time()
        data = []
        bar = tqdm(df.iterrows(), desc="Getting content", total=len(df))
        for i, row in bar:
            data.append(get_content_about_us(row["website"], cache_dir))
            bar.set_description("Getting content: %s" % (row["website"]))
        print("Time not use ray:", str(datetime.timedelta(seconds = int(time.time() - start_time))))
    else:
        start_time = time.time()
        ray.shutdown()
        ray.init(num_cpus=32)
        from progress_bar import ProgressBar
        pb = ProgressBar(len(df))
        task = [get_content_about_us.remote(website, cache_dir, pba=pb.actor) for website in tqdm(df["website"], desc="Adding tasks get_content_about_us")]
        pb.print_until_done()
        data = ray.get(task)
        print("Time use ray:", str(datetime.timedelta(seconds = int(time.time() - start_time))))

    df["content"] = [d["content"] for d in data]
    df["about_us_url"] = [d["about_us_url"] for d in data]
    df["about_us_content"] = [d["about_us_content"] for d in data]
    df = pd.DataFrame(df)
    df.to_csv("data_cbinsights_content.csv", index=False)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--statis", action="store_true", default=False)
    parser.add_argument("--get_content", action="store_true", default=False)
    args = parser.parse_args()
    
    if args.get_content:
        get_content()
    elif args.statis:
        statis_content()
    else:
        print("No argument")
    
if __name__ == "__main__":
    main()