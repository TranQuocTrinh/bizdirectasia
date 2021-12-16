from bs4 import BeautifulSoup
import requests
import string
import re
from tqdm import tqdm
import json
import os
import pandas as pd
import ray

@ray.remote
def get_text_from_url(url, output_dir, timeout=20):
    path = os.path.join(output_dir, url.replace("/","-"))
    if os.path.exists(path):
        res = json.load(open(path))
        return res["text"]
    else:
        if url.split("/")[0] not in {"http:", "https"}:
            try:
                response = requests.get("http://"+url, timeout=timeout)
                text = " ".join(BeautifulSoup(response.text, "html.parser").getText().split())
                res = dict(
                    website=url,
                    text=text
                )
                json.dump(res, open(path, "w"))
                return text
            except:
                pass
            
            try:
                response = requests.get("https://"+url, timeout=timeout)
                text = " ".join(BeautifulSoup(response.text, "html.parser").getText().split())
                res = dict(
                    website=url,
                    text=text
                )
                json.dump(res, open(path, "w"))
                return text
            except:
                text = ""
                res = dict(
                    website=url,
                    text=text
                )
                json.dump(res, open(path, "w"))
                return text
        else:
            try:
                response = requests.get(url, timeout=timeout)
                text = " ".join(BeautifulSoup(response.text, "html.parser").getText().split())
                res = dict(
                    website=url,
                    text=text
                )
                json.dump(res, open(path, "w"))
                return text
            except:
                text = ""
                res = dict(
                    website=url,
                    text=text
                )
                json.dump(res, open(path, "w"))
                return text


def count_results(dir_path="cache_text/", total=333683):
    import time, os, json, datetime
    from tqdm import tqdm
    
    t0 = time.time()
    while True:
        files = os.listdir(dir_path)
        finished = len(files) if len(files) > 0 else 1
        t1 = time.time()
        total_time = datetime.timedelta(seconds=int((t1 - t0)))
        total_time = str(total_time)

        timeperweb = round((t1 - t0)/finished, 3)

        percent = int(finished/total*100)

        have_result = []
        error = 0
        for f in tqdm(files):
            filecachepath = os.path.join(dir_path, f)
            try:
                have_result.append(json.load(open(filecachepath)))
            except:
                os.system(f"rm {filecachepath}")
                error += 1
        have_result = [d for d in have_result if d["text"]]
        have_result = len(have_result)

        have_result_precent = int(have_result/finished*100)

        remain_time = int(timeperweb*(total-finished))
        remain_time = datetime.timedelta(seconds=remain_time)
        remain_time = str(remain_time)

        os.system('clear')
        print("--------- STEP 1: GET CONTENT OF WEBSITE ---------")
        print(f"Finished: {finished}")
        print(f"Total: {total}")
        print(f"Time/website: {timeperweb}s/it")
        print(f"Percent: {percent}%")
        print(f"Total time: {total_time}")
        print()        
        print(f"Have result: {have_result}")
        print(f"Percent: {have_result_precent}%")
        print(f"Error: {error}")
        print(f"Estimated time remaining: {remain_time}")
        time.sleep(5)
        if finished >= total:
            break


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", default="query_text", type=str, required=True, help="Task for runing in {'query_text', 'report'}",)
    parser.add_argument("--num_thread", default=8, type=int, required=False, help="Number of cpus for query_text task",)
    parser.add_argument("--cache_dir", default="cache_text", type=str, required=False, help="Directory for cache text",)
    parser.add_argument("--domain_path", default="newzealand.txt", type=str, required=False, help="Path of file list of domain",)
    args = parser.parse_args()
    
    if not os.path.exists(args.cache_dir):
        os.mkdir(args.cache_dir)
    print(args)
    
    lst_domain = [x for x in open(args.domain_path, "r").read().split("\n") if x]

    if args.task == "report":
        count_results(dir_path=args.cache_dir, total=len(lst_domain))
        return
    else:
        ray.shutdown()
        ray.init(num_cpus=args.num_thread)
        task = [get_text_from_url.remote(url=website, output_dir=args.cache_dir, timeout=30) for website in lst_domain]
        results = ray.get(task)
        return

if __name__ == "__main__":
    main()