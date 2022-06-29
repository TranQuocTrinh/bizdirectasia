import bs4 as bs
import urllib.request
import re
import nltk
from utils import preprocess_text
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest

def textsum_nltk(article_text, num_sents=3):
    # Processing
    # Removing Square Brackets and Extra Spaces
    article_text = re.sub(r'\[[0-9]*\]', ' ', article_text)
    article_text = re.sub(r'\s+', ' ', article_text)
    # Removing special characters and digits
    formatted_article_text = re.sub('[^a-zA-Z]', ' ', article_text )
    formatted_article_text = re.sub(r'\s+', ' ', formatted_article_text)

    # preprocess text
    article_text = preprocess_text(article_text)


    # Converting Text To Sentences
    sentence_list = nltk.sent_tokenize(article_text)
    if len(sentence_list) < num_sents:
        num_sents = len(sentence_list)
    
    # Find Weighted Frequency of Occurrence
    stopwords = nltk.corpus.stopwords.words('english')

    word_frequencies = {}
    for word in nltk.word_tokenize(formatted_article_text):
        if word not in stopwords:
            if word not in word_frequencies.keys():
                word_frequencies[word] = 1
            else:
                word_frequencies[word] += 1

    maximum_frequncy = max(word_frequencies.values())

    for word in word_frequencies.keys():
        word_frequencies[word] = (word_frequencies[word]/maximum_frequncy)

    # Calculating Sentence Scores
    sentence_scores = {}
    for sent in sentence_list:
        for word in nltk.word_tokenize(sent.lower()):
            if word in word_frequencies.keys():
                if len(sent.split(' ')) < 30:
                    if sent not in sentence_scores.keys():
                        sentence_scores[sent] = word_frequencies[word]
                    else:
                        sentence_scores[sent] += word_frequencies[word]

    # Getting the Summary
    import heapq
    summary_sentences = heapq.nlargest(3, sentence_scores, key=sentence_scores.get)

    summary = ' '.join(summary_sentences)
    return summary

def textsum_spacy(text, num_sents=3):
    text = preprocess_text(text)
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



from gensim.summarization import summarize

def textsum_getsim(text):
    summ = summarize(text, word_count=100 if len(text.split(' ')) > 100 else len(text.split(' ')))
    return summ

# from pyteaser import Summarize
# def textsum_teaser(text, num_sents=3):
#     summ = Summarize('',text)
#     return summ

from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
from sumy.summarizers import luhn
from sumy.summarizers.luhn import LuhnSummarizer
from sumy.summarizers.lsa import LsaSummarizer

def textsum_lex(text, num_sents=3):
    text = preprocess_text(text)
    LANGUAGE = "english"
    parser = PlaintextParser.from_string(text, Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)
    summarizer = LexRankSummarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)
    summ = " ".join([str(sentence) for sentence in summarizer(parser.document, num_sents)])
    return summ

def textsum_lsa(text, num_sents=3):
    text = preprocess_text(text)
    LANGUAGE = "english"
    parser = PlaintextParser.from_string(text, Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)
    summarizer = LsaSummarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)
    summ = " ".join([str(sentence) for sentence in summarizer(parser.document, num_sents)])
    return summ

def textsum_luhn(text, num_sents=3):
    text = preprocess_text(text)
    LANGUAGE = "english"
    parser = PlaintextParser.from_string(text, Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)
    summarizer = LuhnSummarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)
    summ = " ".join([str(sentence) for sentence in summarizer(parser.document, num_sents)])
    return summ


from tqdm import tqdm
import pandas as pd
df = pd.read_csv("/home/pvduy/tqtrinh/bizdirectasia/website2description/data_collect/run_mass/content/singapore_content.csv")
df = df[df["content"].isnull()==False]
df = df[df["language"]=="en"]
df["len"] = df["content"].apply(len)
df = df[df["len"]>200].sample(n=500, random_state=42).reset_index(drop=True)

df["summary_nltk"] = ""
df["summary_spacy"] = ""
df["summary_getsim"] = ""
df["summary_lex"] = ""
df["summary_lsa"] = ""
df["summary_luhn"] = ""

for i,r in tqdm(df.iterrows(), total=len(df), desc="textsum"):
    content = r["content"]
    try:
        df.loc[i, "summary_nltk"] = textsum_nltk(content)
    except:
        df.loc[i, "summary_nltk"] = "error"
    try:
        df.loc[i, "summary_spacy"] = textsum_spacy(content)
    except:
        df.loc[i, "summary_spacy"] = "error"
    try:
        df.loc[i, "summary_getsim"] = textsum_getsim(content)
    except:
        df.loc[i, "summary_getsim"] = "error"
    try:
        df.loc[i, "summary_lex"] = textsum_lex(content)
    except:
        df.loc[i, "summary_lex"] = "error"
    try:
        df.loc[i, "summary_lsa"] = textsum_lsa(content)
    except:
        df.loc[i, "summary_lsa"] = "error"
    try:
        df.loc[i, "summary_luhn"] = textsum_luhn(content)
    except:
        df.loc[i, "summary_luhn"] = "error"

df = df[['company_id', 'company_key', 'company_name', 'website', 'content', 'summary_nltk', 'summary_spacy', 'summary_getsim', 'summary_lex', 'summary_lsa', 'summary_luhn']]
df.to_csv("500_singapore_content_summary.csv", index=False)
