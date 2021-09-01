from nltk import text
from extract_link import get_all_website_links
import os
import boto3
import json
from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup 
import pandas as pd
from tqdm import tqdm
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from langdetect import detect

import spacy
nlp = spacy.load("en_core_web_sm")


options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")

TIME_OUT = 30 # 5 seconds

CACHE_DIR = "cache_data"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)
comprehend = boto3.client(service_name='comprehend', region_name='us-east-2')


import nltk
import re
import string

def clean_text(text):
    text = text.lower()
    text = re.sub('https?://\S+|www\.\S+', '', text)
    punctuation_remove = re.sub('[%s]' % re.escape("_,.!?'"), '', string.punctuation)
    text = re.sub('[%s]' % re.escape(punctuation_remove), '', text)
    text = re.sub('\w*\d\w*', '', text)
    return text


def process_text(text):
    soup = BeautifulSoup(text, "lxml")
    new_text = soup.getText(strip=True)
    new_text = ' '.join([w for w in new_text.split() if len(w) < 10])
    return clean_text(new_text)

# def get_text_url(domain):
#     if "http:" not in domain.split("/") and "https:" not in domain.split("/"):
#         driver = webdriver.Chrome(chrome_options=options)
#         driver.set_page_load_timeout(TIME_OUT)
#         try:
#             url = "http://" + domain
#             driver.get(url)
#             return driver.page_source, url
#         except TimeoutException:
#             url = "https://" + domain
#             driver.get(url)
#             return driver.page_source, url
#         except:
#             driver.close()
#             return "", domain
#     else:
#         driver = webdriver.Chrome(chrome_options=options)
#         driver.set_page_load_timeout(TIME_OUT)
#         try:
#             driver.get(domain)
#             return driver.page_source, domain
#         except:
#             driver.close()
#             return "", domain

def get_text_url(domain):
    if "http:" not in domain.split("/") and "https:" not in domain.split("/"):
        try:
            url = "http://" + domain
            content = requests.get(url).content
            return content, url
        except requests.exceptions.Timeout:
            url = "https://" + domain
            content = requests.get(url).content
            return content, url
        except:
            return "", domain
    else:
        try:
            content = requests.get(domain).content
            return content, domain
        except:
            return "", domain

def extract_url_level1(domain):
    webcontent, url = get_text_url(domain)
    soup = BeautifulSoup(webcontent, "lxml")
    urls = []
    if webcontent != "":
        url_level1 = get_all_website_links(url=url, soup=soup)
        for link in url_level1:
            link_split = link.split('/')
            condition1 = link[-1] != '/' and len(link_split) == 4
            condition2 = link[-1] == '/' and len(link_split) == 5
            condition3 = link[0] == '/' and len(link_split) == 2
            condition4 = link_split[0] in {'http:', 'https:'}
            if (condition1 or condition2 or condition3) and condition4:
                urls.append('/'.join(link_split))
    # filter url

    return urls
        

def extract_text_from_url(domain, min_num_tokens=20):
    file_path = f"{CACHE_DIR}/{domain.replace('/','_')}.json"
    if os.path.exists(file_path):
        print(f"Cache text {file_path}")
        response = json.load(open(file_path))
        text_clean = response["OriginalText"]
    else:
        """
        url = domain
        if "http:" not in url.split("/") and "https:" not in url.split("/"):
            url = "http://" + url

        
        #url = "https://vingroup.net/"
        # way1
        if "http:" not in url.split("/") and "https:" not in url.split("/"):
            url = "http://" + url

        # try:
        # res = requests.get(url)
        # html_page = res.content
        # soup = BeautifulSoup(html_page, "html.parser")
        # except:
        # # way2
        html = urlopen(url).read()
        soup = BeautifulSoup(html, "lxml")
        
        driver = webdriver.Chrome(chrome_options=options)
        driver.set_page_load_timeout(TIME_OUT)
        try:
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, "lxml")
            driver.close()
        except TimeoutException:
            driver.close()
            return "timeout"
        except:
            driver.close()
            return "error"
        """
        
        webcontent, url = get_text_url(domain)
        if webcontent == "":
            return "timeout"
        else:
            soup = BeautifulSoup(webcontent, "lxml")
        
        lst_text = soup.find_all(text=True)
        
        lst_text_clean = [] 
        blacklist = ["[document]", "noscript", "header", "html", "meta", "head", "input", "script", "style"]
        for text in lst_text: 
            if text.parent.name not in blacklist:
                text_split = text.split()
                if len(text_split) > min_num_tokens:
                    # text = text.replace("\n", " ")
                    text = " ".join(text.split())
                    lst_text_clean.append(text)
        
        lst_text_clean = [process_text(text) for text in lst_text_clean]
        text_clean = "\n".join(lst_text_clean)
        # For aws
        while len(text_clean.encode('utf-8')) > 5000:
            new = [text for text in lst_text_clean if len(text.split()) > min_num_tokens]
            text_clean = "\n".join(new)
            min_num_tokens += 1
    return str(text_clean.encode('utf-8'))


def ner_aws(text, domain):
    file_path = f"{CACHE_DIR}/{domain.replace('/','_')}.json"
    if os.path.exists(file_path):
        print(f"Cache aws {file_path}")
        response = json.load(open(file_path))
        if response["OriginalText"] in {"error", "timeout", ""}:
            return []
    else:
        if text in {"error", "timeout", ""}:
            json.dump({"OriginalText": text}, open(file_path, "w"))
            return []

        lang = detect(text)
        if lang not in ["ar", "hi", "ko", "zh-TW", "ja", "zh", "de", "pt", "en", "it", "fr", "es"]:
            lang_call = "en"
        else:
            lang_call = lang

        response = comprehend.detect_entities(
            Text=text,
            LanguageCode=lang_call
        )
        response["OriginalText"] = text
        response["LanguageCode"] = lang
        json.dump(response, open(file_path, "w"))

    ner_result = [(e['Text'], e['Type']) for e in response['Entities']]
    return ner_result


def ner_spacy_noun_phrase(text):
    doc = nlp(text)
    ner = [(ent.text, ent.label_) for ent in doc.ents]
    noun_phrase = [chunk.text for chunk in doc.noun_chunks]

    return ner, noun_phrase


def main():
    df = pd.read_csv("sample_domain.csv")[:100]
    dfout = []
    # try:
    bar = tqdm(df.iterrows(), total=len(df))
    for i,r in bar:
        domain = r["domain"]
        
        lst_urls = [domain] + extract_url_level1(domain=domain)
        lst_urls = lst_urls[:10]
        print(lst_urls)
        for idx, url in enumerate(lst_urls):
            print(f"[{idx+1}]/[{len(lst_urls)}]")
            text = extract_text_from_url(domain=url, min_num_tokens=10)
            lang = detect(text)
            if lang != "en":
                temp = {
                    'index': f"{i}-{idx}",
                    'url': url,
                    'text_tract': text,
                    'language': lang,
                    'noun_phrase': '',
                    'ner_aws': '',
                    'ner_org': '',
                }
                print('Not English!')
            else:
                ner_spacy, noun_phrase = ner_spacy_noun_phrase(text)
                ner_result = ner_aws(' '.join(noun_phrase), url)
                temp = {
                    'index': f"{i}-{idx}",
                    'url': url,
                    'text_tract': text,
                    'language': lang,
                    'noun_phrase': noun_phrase,
                    'ner_aws': ner_result,
                    'ner_org': ner_spacy,
                }
                print(ner_spacy)
            dfout.append(temp)
        bar.set_description(f"domain: {domain}")
    dfout = pd.DataFrame(dfout)
    dfout.to_csv(f"sample_domain_extract-text_noun-phrase_ner_{len(dfout)}.csv", index=False)
    # except:
    #     dfout = pd.DataFrame(dfout)
    #     dfout.to_csv(f"sample_domain_extract-text_noun-phrase_ner_{len(dfout)}.csv", index=False)
    import ipdb; ipdb.set_trace()

if __name__ == "__main__":
    # print(extract_url_level1(domain="https://bizdirectasia.com"))
    # text_extract = extract_text_from_url("https://bizdirectasia.com")
    # print("text_extract", text_extract)
    # print(ner_spacy_noun_phrase(text_extract))
    main()
    # print(extract_url_level1(domain="djenterprisemehsana.com/"))