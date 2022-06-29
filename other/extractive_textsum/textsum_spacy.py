import bs4 as bs
import urllib.request
import re
import nltk
from utils import get_content_company, preprocess_text
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest

# article_text = get_content_company("https://bizdirectasia.com/")
def textsum(text, num_sents=3):
    nlp = spacy.load('en_core_web_sm')
    doc= nlp(text)
    tokens=[token.text for token in doc]
    word_frequencies={}
    for word in doc:
        if word.text.lower() not in list(STOP_WORDS):
            if word.text.lower() not in punctuation:
                if word.text not in word_frequencies.keys():
                    word_frequencies[word.text] = 1
                else:
                    word_frequencies[word.text] += 1
    max_frequency=max(word_frequencies.values())
    for word in word_frequencies.keys():
        word_frequencies[word]=word_frequencies[word]/max_frequency
    sentence_tokens= [sent for sent in doc.sents]
    sentence_scores = {}
    for sent in sentence_tokens:
        for word in sent:
            if word.text.lower() in word_frequencies.keys():
                if sent not in sentence_scores.keys():                            
                    sentence_scores[sent]=word_frequencies[word.text.lower()]
                else:
                    sentence_scores[sent]+=word_frequencies[word.text.lower()]

    summary = nlargest(num_sents, sentence_scores,key=sentence_scores.get)
    final_summary=[word.text for word in summary]
    summary=''.join(final_summary)
    return summary


from tqdm import tqdm
import pandas as pd
df = pd.read_csv("/home/pvduy/tqtrinh/bizdirectasia/website2description/data_collect/run_mass/content/singapore_content.csv")
df = df[df["content"].isnull()==False]
df = df[df["language"]=="en"]
df["len"] = df["content"].apply(len)
df = df[df["len"]>200].sample(n=10000, random_state=42).reset_index(drop=True)

lst_summary = []
for i,r in tqdm(df.iterrows(), total=len(df), desc="textsum"):
    content = r["content"]
    lst_summary.append(textsum(content))
df["summary"] = lst_summary
df = df[['company_id', 'company_key', 'company_name', 'website', 'content', 'summary']]
df.to_csv("10k_singapore_content_summary_spacy.csv", index=False)