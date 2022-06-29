import bs4 as bs
import urllib.request
import re
import nltk
from utils import get_content_company, preprocess_text


# article_text = get_content_company("https://bizdirectasia.com/")
def textsum(article_text, num_sents=3):
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
df.to_csv("10k_singapore_content_summary.csv", index=False)