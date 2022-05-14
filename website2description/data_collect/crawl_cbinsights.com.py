from bs4 import BeautifulSoup
import requests
import re
import json
import os
from tqdm import tqdm
import ray
import time
import datetime
import pandas as pd


def crawl_by_sitemap(url="https://www.cbinsights.com/sitemap/sitemap_master.xml"):
    if os.path.exists("list_cbinsights_companies.json"):
        company_urls = json.load(open("list_cbinsights_companies.json"))
    else:
        sitemap = requests.get(url)
        soup = BeautifulSoup(sitemap.text, "xml")
        urls = [url.text for url in soup.find_all("loc") if "company" in url.text]

        print("Found {} urls".format(len(urls)))

        company_urls = []
        for url in tqdm(urls):
            soup = BeautifulSoup(requests.get(url).text, "xml")

            company_urls.extend([url.text for url in soup.find_all("loc")])

    print("Found {} company urls".format(len(company_urls)))
    return company_urls


@ray.remote
def get_company_description_website(url, cache_dir="cache", pba=None):
    cache_file = os.path.join(cache_dir, "{}.json".format(url.split("/")[-1]))
    if os.path.exists(cache_file):
        rep = json.load(open(cache_file))
        if rep["description"] != "":
            return rep

    res = requests.get(url)
    if res.status_code == 200:
        soup = BeautifulSoup(res.content, "html.parser")
        description = soup.find(class_="CompanyInfo_about__ixE_1")
        description = description.find("p").getText() if description else ""
        website = soup.find("a", class_="Header_companyLink__7lw2L")
        website = website.get("href") if website else ""
        company_name = soup.find("h1").getText()
        rep = {
            "description": description,
            "website": website,
            "source": "cbinsights.com",
            "url": url,
            "company_name": company_name,
        }
        json.dump(rep, open(cache_file, "w"))
    else:
        rep = {
            "description": "",
            "website": "",
            "source": "cbinsights.com",
            "url": url,
            "company_name": "",
        }
        json.dump(rep, open(cache_file, "w"))
    if pba is not None:
        pba.update.remote(1)
    return rep


def crawl_cbinsights():
    cache_dir = "cache_cbinsights"
    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)
    
    company_urls = crawl_by_sitemap()

    if 0:
        df = []
        bar = tqdm(enumerate(company_urls), total=len(company_urls), desc="Crawling")
        statis = {
            "description": 0,
            "website": 0,
            "company_name": 0,
            "total": len(company_urls),
        }
        for i,url in bar:
            data = get_company_description_website(url, cache_dir)
            statis["description"] += 1 if data["description"] != "" else 0
            statis["website"] += 1 if data["website"] != "" else 0
            statis["company_name"] += 1 if data["company_name"] != "" else 0
            if i % 1000 == 0:
                bar.set_postfix(description=statis["description"], website=statis["website"], company_name=statis["company_name"], total=statis["total"])
            df.append(data)
    else:
        start_time = time.time()
        ray.shutdown()
        from progress_bar import ProgressBar
        pb = ProgressBar(len(company_urls))
        task = [get_company_description_website.remote(url, cache_dir, pba=pb.actor) for url in tqdm(company_urls, desc="Adding tasks")]
        pb.print_until_done()
        df = ray.get(task)
        print("Time use ray:", str(datetime.timedelta(seconds = int(time.time() - start_time))))

    df = pd.DataFrame(df)
    df.to_csv("data_cbinsights.csv", index=False)
    

def statis_cbinsights(cache_dir="cache_cbinsights"):
    files = set()
    company_urls = crawl_by_sitemap()
    df = []
    while True:
        curr_files = set(os.listdir(cache_dir))
        for f in curr_files:
            if f not in files:
                df.append(json.load(open(os.path.join(cache_dir, f))))
                files.add(f)
        
        os.system("clear")
        res_df = pd.DataFrame(df).fillna("")
        print("Total:", len(company_urls))
        num_des = len(res_df[res_df["description"] != ""])
        print("Description: {} | Percentage: {:.2f}%".format(num_des, num_des/len(files)*100))
        num_website = len(res_df[res_df["website"] != ""])
        print("Website: {} | Percentage: {:.2f}%".format(num_website, num_website/len(files)*100))
        num_company_name = len(res_df[res_df["company_name"] != ""])
        print("Company name: {} | Percentage: {:.2f}%".format(num_company_name, num_company_name / len(files) * 100))
        time.sleep(1)
        if len(files) == len(company_urls):
            break


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--statis_cbinsights", action="store_true", default=False)
    parser.add_argument("--crawl", action="store_true", default=False)
    parser.add_argument("--get_content", action="store_true", default=False)
    args = parser.parse_args()
    if args.crawl:
        crawl_cbinsights()
    elif args.statis_cbinsights:
        statis_cbinsights()
    else:
        print("No argument")