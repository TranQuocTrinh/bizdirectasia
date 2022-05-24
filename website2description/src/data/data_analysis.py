#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from tqdm import tqdm

train_df, val_df, test_df = pd.read_csv("train.csv"), pd.read_csv("val.csv"), pd.read_csv("test.csv")
train_df[["website", "content", "description"]].head()


# In[2]:

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

    return processed_text

# In[11]:


def print_idx(df, idx):
    print("------ Website:", df.iloc[idx]["website"])
    print("------ Content:", df.iloc[idx]["content"])
    print("------ Description:", df.iloc[idx]["description"])


# In[4]:


def num_words_description_contained_content(description, content):
    description = set(description.split())
    content = set(content.split())
    return len(description & content)


# In[23]:


def process_csv_data(df):
    columns = df.columns
    df["content_tmp"] = [preprocess_text(x) for x in tqdm(df["content"].values, desc="Process content...")]
    df["num_words_des"] = df["description"].apply(lambda x: len(set(x.split())))
    df["num_words_content"] = df["content_tmp"].apply(lambda x: len(set(x.split())))
    df["num_words_des_contained_content"] = df.apply(lambda x: num_words_description_contained_content(x["description"], x["content_tmp"]), axis=1)
    df = df[df["num_words_des"] < 100]
    df = df[df["num_words_des"] > 5]
    df["ratio"] = df["num_words_des_contained_content"] / df["num_words_des"]
    df = df[df["ratio"] >= 0.45]
    df = df[df["num_words_content"] > df["num_words_des"]]
    df = df.reset_index(drop=True)
    return df[columns]


# In[6]:


train_df = process_csv_data(train_df)
val_df = process_csv_data(val_df)
test_df = process_csv_data(test_df)
train_df.to_csv("train_filtered.csv", index=False)
val_df.to_csv("val_filtered.csv", index=False)
test_df.to_csv("test_filtered.csv", index=False)
print("Train data:", train_df.shape)
print("Val data:", val_df.shape)
print("Test data:", test_df.shape)
