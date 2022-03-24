from bs4 import BeautifulSoup
import requests
import string
import re
from tqdm import tqdm
import json
import os
import pandas as pd


def get_text_from_url(url, output_dir=None, timeout=20, paragraph=False):
    def get_parapgraphs(soup):
        paragraphs = []
        paragraphs_set = set()
        for paragraph in soup.find_all('p'):
            if paragraph.text not in paragraphs_set and len(paragraph.text) > 100:
                paragraphs_set.add(paragraph.text)
                paragraphs.append(paragraph.text)
        return paragraphs

    def get_text(url):
        if url.split("/")[0] not in {"http:", "https:"}:
            try:
                response = requests.get("http://"+url, timeout=timeout)
                soup = BeautifulSoup(response.content, 'html.parser')
                text = "\n".join(get_parapgraphs(soup)) if paragraph else soup.get_text()
                return text
            except:
                pass
            
            try:
                response = requests.get("https://"+url, timeout=timeout)
                soup = BeautifulSoup(response.content, 'html.parser')
                text = "\n".join(get_parapgraphs(soup)) if paragraph else soup.get_text()
                return text
            except:
                text = ""
                return text
        else:
            try:
                response = requests.get(url, timeout=timeout)
                soup = BeautifulSoup(response.content, 'html.parser')
                text = "\n".join(get_parapgraphs(soup)) if paragraph else soup.get_text()
                return text
            except:
                text = ""
                return text

    if output_dir is not None:
        path = os.path.join(output_dir, url.replace("/","-"))
        if os.path.exists(path):
            res = json.load(open(path))
        else:
            text = get_text(url)
            res = dict(
                website=url,
                text=text
            )
            json.dump(res, open(path, "w"))
    else:
        text = get_text(url)
        res = dict(
            website=url,
            text=text
        )
    
    return res["text"]


def load_model_tokenizer(model_base="sshleifer/distilbart-cnn-6-6"):
    from transformers import BartForConditionalGeneration, BartTokenizer

    model = BartForConditionalGeneration.from_pretrained(model_base)
    tokenizer = BartTokenizer.from_pretrained(model_base)

    return model, tokenizer

def summarize(model, tokenizer, lst_text):
    batch = tokenizer(lst_text, max_length=1024, truncation=True, return_tensors="pt")
    generated_ids = model.generate(batch["input_ids"], max_length=128, temperature=0.7, repetition_penalty=1.2, top_k=50, top_p=0.95)
    generated = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
    return generated

def load_model_fb():
    from transformers import pipeline
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    return summarizer

def summarize_fb(summarizer, text):
    return summarizer(text, max_length=150, min_length=100, do_sample=False)

def temp():
    from transformers import PegasusForConditionalGeneration, PegasusTokenizer
    import torch

    src_text = [
        """ PG&E stated it scheduled the blackouts in response to forecasts for high winds amid dry conditions. The aim is to reduce the risk of wildfires. Nearly 800 thousand customers were scheduled to be affected by the shutoffs which were expected to last through at least midday tomorrow."""
    ]

    model_name = "google/pegasus-xsum"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = PegasusTokenizer.from_pretrained(model_name)
    model = PegasusForConditionalGeneration.from_pretrained(model_name).to(device)
    batch = tokenizer(src_text, truncation=True, padding="longest", return_tensors="pt").to(device)
    translated = model.generate(**batch)
    tgt_text = tokenizer.batch_decode(translated, skip_special_tokens=True)
    assert (
        tgt_text[0]
        == "California's largest electricity provider has turned off power to hundreds of thousands of customers."
    )


from google.cloud import language
from os import environ
environ["GOOGLE_APPLICATION_CREDENTIALS"] = "web-architecture-migration-quoc-trinh.json"
def analyze_text_syntax(text):
    client = language.LanguageServiceClient()
    document = language.Document(content=text, type_=language.Document.Type.PLAIN_TEXT)

    response = client.analyze_syntax(document=document)
    
    # convert response to json
    import json
    result_json = response.__class__.to_json(response)
    result_dict = json.loads(result_json)

    # fmts = "{:10}: {}"
    # print(fmts.format("sentences", len(response.sentences)))
    # print(fmts.format("tokens", len(response.tokens)))
    # for i, token in enumerate(response.tokens):
    #     print(fmts.format(token.part_of_speech.tag.name, token.text.content))
    analyze = []
    for i, token in enumerate(response.tokens):
        analyze.append((token.part_of_speech.tag.name, token.text.content))

    noun_phrase_list = []
    current_idx = 0
    for i,token in enumerate(response.tokens):
        if token.part_of_speech.tag.name in {"NUM", "NOUN"} and i >= current_idx:
            j = i + 1
            while j < len(response.tokens) and response.tokens[j].part_of_speech.tag.name == "NOUN" and response.tokens[j].text.content != ".":
                j += 1
            lst_noun = [token.text.content for token in response.tokens[i:j]]
            if len(lst_noun) > 1:
                noun_phrase_list.append(" ".join(lst_noun))
            current_idx = j
    print(noun_phrase_list)

    return result_dict, analyze, noun_phrase_list


def main():
    df = {"website": [], "content": [], "summary": [], "analyze": [], "noun_phrase_list": []}
    # url_list = ["https://bizdirectasia.com/", "https://stackoverflow.com/"]
    url_list = open("/home/ubuntu/tqtrinh/web2contact_matching/domain/networksdb.io-domains_sg.txt").read()
    url_list = [url for url in url_list.split("\n") if url != ""][:1000]
    model_fb = load_model_fb()
    # model, tokenizer = load_model_tokenizer("sshleifer/distilbart-cnn-12-6")

    for i, url in enumerate(url_list):
        content = get_text_from_url(url, paragraph=True)
        # summary = summarize(model, tokenizer, [text])[0]
        try:
            summary_fb = summarize_fb(model_fb, content)
        except:
            summary_fb, analyze, noun_phrase_list = "", [], []
        res, analyze, noun_phrase_list = analyze_text_syntax(content)
        df["website"].append(url)
        df["content"].append(content)
        df["summary"].append(summary_fb)
        df["analyze"].append(analyze)
        df["noun_phrase_list"].append(noun_phrase_list)
    
    df = pd.DataFrame(df)
    print(df)
    df.to_csv("100_urls_singapore_extract_keyword.csv")
    import ipdb; ipdb.set_trace()

if __name__ == "__main__":
    main()