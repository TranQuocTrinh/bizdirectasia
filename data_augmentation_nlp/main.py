import requests
import json
from bs4 import BeautifulSoup
import re
import os
import random
import pandas as pd


def get_url():
    soup = BeautifulSoup(requests.get("https://www.wisebread.com/sitemap.xml?page=1").text, 'xml')
    urls = []
    for url in soup.find_all('loc')[1:]:
        urls.append(url.text)
    return urls

def get_content_seo(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.find('h1', class_="page-title").text
    content = soup.find('div', class_="body")
    tags = ["p", "h2", "h3", "ul", "ol", "li", "strong", "em", "a"]
    content_str = []
    for tag in content.find_all(recursive=False):
        if str(tag.name) in tags:
            content_str.append(tag.get_text())
    
    content_str = "\n".join(content_str)
    seo = {
        "url": url,
        "title": title,
        "content": content_str
    }
    return seo

def create_df_example():
    df = []
    urls = get_url()
    for url in random.choices(urls, k=10):
        seo = get_content_seo(url)
        df.append(seo)
    df = pd.DataFrame(df)
    df.to_csv("seo_content_example.csv", index=False)


def main():
    from augmenter import Augmenter
    from tqdm import tqdm

    augter = Augmenter()
    df = pd.read_csv("seo_content_example.csv")
    for method in tqdm(["pegasus_paraphrase", "synonym", "back_translate", "contextual_word", "random"]):
        df[f"augmented_content_{method}"] = [augter.augment(x["content"], method, ratio=1.0) for i,x in tqdm(df.iterrows(), total=len(df), desc=f"{method}")]
        df.to_csv("seo_content_example_augmented.csv", index=False)
    print(df.head())

if __name__ == "__main__":
    main()