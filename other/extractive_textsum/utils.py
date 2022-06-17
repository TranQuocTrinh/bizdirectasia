import requests
import requests.exceptions as reqex
import json
import os
import time
import pandas as pd
from boilerpy3 import extractors, exceptions


def get_html_from_url(website, output_dir="", timeout=10):
    st = time.time()
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




import nltk
from transformers.utils import is_offline_mode
from filelock import FileLock
import re
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from bs4 import BeautifulSoup

try:
    nltk.data.find("tokenizers/punkt")
except (LookupError, OSError):
    if is_offline_mode():
        raise LookupError(
            "Offline mode: run this script without TRANSFORMERS_OFFLINE first to download nltk data files"
        )
    with FileLock(".lock") as lock:
        nltk.download("punkt", quiet=True)


def preprocess_text(text):
    def clean_html(html):
        soup = BeautifulSoup(html, "html.parser")
        for data in soup(['style', 'script', 'code', 'a']):
            data.decompose()
        return ' '.join(soup.stripped_strings)
    # remove words with length > 20
    text = re.sub(r'\b\w{11,}\b', '', text)

    processed_text = str(text).strip()
    # clean html
    processed_text = clean_html(processed_text)
    # remove text between { and }
    processed_text = re.sub(r"\{.*?\}", "", processed_text)
    # remove text between [ and ]
    processed_text = re.sub(r"\[.*?\]", "", processed_text)
    # remove repeated punctuation
    def remove_repeated_punctuation(text):
        return re.sub(r"([,!?!\"#$%&\'\(\)*+,-./:;<=>?@\[\\\]^_`\{|\}~])\1+", r"\1", text)
    
    # tokenize
    processed_text = word_tokenize(processed_text)
    processed_text = ' '.join(processed_text)
    # remove non-ascii characters
    processed_text = re.sub(r'[^\x00-\x7F]+', ' ', processed_text)
    # remove duplicate punctuation
    processed_text = re.sub(r'([!?,.()])\1+', r'\1', processed_text)
    # remove spaces before punctuation
    processed_text = re.sub(r'\s+([!?,.()])', r'\1', processed_text)
    # remove spaces
    processed_text = " ".join(processed_text.split())
    # remove all single characters
    processed_text = re.sub(r'\s+[a-zA-Z]\s+', ' ', processed_text)
    # Remove single characters from the start
    processed_text = re.sub(r'\^[a-zA-Z]\s+', ' ', processed_text)
    # Substituting multiple spaces with single space
    processed_text = re.sub(r'\s+', ' ', processed_text)
    # Removing prefixed 'b'
    processed_text = re.sub(r'^b\s+', '', processed_text)
    # Lemmatization
    processed_text = processed_text.split()
    lemmatizer = WordNetLemmatizer()
    processed_text = [lemmatizer.lemmatize(word) for word in processed_text]
    processed_text = ' '.join(processed_text)
    processed_text = remove_repeated_punctuation(processed_text)
    processed_text = " ".join(processed_text.split())
    processed_text = processed_text.replace("( ", " (").replace(" :", ":").replace(" `", "`").replace(" ;", ";").replace(" '", "'") 

    return processed_text