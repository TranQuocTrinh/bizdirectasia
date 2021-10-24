import joblib
import json
import argparse
from tqdm import tqdm
import pandas as pd
from bs4 import BeautifulSoup
import requests
import os

import string
import re


def clean_text(text):
    text = text.lower()
    text = re.sub('\[.*?\]', ' ', text)
    text = re.sub('\(.*?\)', ' ', text)
    text = re.sub('<.*?>', ' ', text)
    text = re.sub('/.*?/', ' ', text)
    printable = set(string.printable)
    text = ''.join(filter(lambda x: x in printable, text))
    text = ' '.join(text.split())
    return text


def craw_wiki():
    keywords = list(pd.read_csv("keyword.csv")["keyword"])

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--num_thread",
                        help="How many parts is the data divided?", default=1)
    parser.add_argument(
        "-t", "--thread", help="what part of the data?", default=0)
    args = parser.parse_args()

    number_samples = len(keywords)//int(args.num_thread)
    from_idx = number_samples * int(args.thread)
    if int(args.thread) == int(args.num_thread)-1:
        to_idx = len(keywords)
    else:
        to_idx = number_samples*(int(args.thread)+1)
    keywords = keywords[from_idx:to_idx]

    df = []
    count = 0
    bar = tqdm(enumerate(keywords), total=len(keywords))
    for i, k in bar:
        k = k.strip()
        path = f'cache/{k.replace(" ","_").replace("/","-")}.json'
        if not os.path.exists(path):
            try:
                soup = BeautifulSoup(requests.get(
                    f"https://en.wikipedia.org/wiki/{k.replace(' ', '_')}").text, "html.parser")
                text = "\n".join([x.getText().strip("\n")
                                  for x in soup.find_all("p")[:3]]).strip("\n")
                text = " ".join(text.split())
                count += 1
                temp = {
                    "keyword": k,
                    "wiki": text
                }
                json.dump(temp, open(path, "w"))
            except:
                temp = {
                    "keyword": k,
                    "wiki": "unknown"
                }
        else:
            temp = json.load(open(path))

        print(f"keyword: {temp['keyword']}")
        print(f"wiki: {temp['wiki']}")
        print(f"clean_wiki: {clean_text(temp['wiki'])}")

        df.append(temp)
        bar.set_postfix(have=count, total=i+1)

    # df = pd.DataFrame(df)
    fname = f"result_wiki_{args.num_thread}_{args.thread}"
    json.dump(df, open(fname+".json", "w"))
    # joblib.dump(df, fname+".joblib")
    # df.to_csv(fname, index=False)

# filter dataset


def filter_data():
    fname = f"result_wiki_1_0.json"
    lst = json.load(open(fname))

    new_lst = []
    bar = tqdm(lst)
    delup = set()
    for d in bar:
        condition1 = d["wiki"] == "unknown"
        condition2 = len(d["wiki"].split()) < 15
        condition3 = len(d["wiki"].split()) > 250
        condition4 = d["wiki"] in delup
        condition5 = d["wiki"].find("refer to:") != -1
        if condition1 or condition2 or condition3 or condition4 or condition5:
            pass
        else:
            new_lst.append(d)
            delup.add(d["wiki"])
        bar.set_postfix(length=len(new_lst), all=len(lst))

    df = pd.DataFrame(new_lst)
    if df.shape[0] != 0:
        df.to_csv("data_training_key2blog.csv", index=False)
    print(df.shape)


if __name__ == "__main__":
    filter_data()
