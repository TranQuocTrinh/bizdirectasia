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


def main():
    url = "https://bizdirectasia.com/"
    text = get_text_from_url(url, paragraph=True)
    model, tokenizer = load_model_tokenizer("sshleifer/distilbart-cnn-12-6")
    summary = summarize(model, tokenizer, [text])[0]


    model_fb = load_model_fb()
    summary_fb = summarize_fb(model_fb, text)


from google.cloud import language
environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join("web-architecture-migration-quoc-trinh.json")
def analyze_text_syntax(text):
    client = language.LanguageServiceClient()
    document = language.Document(content=text, type_=language.Document.Type.PLAIN_TEXT)

    response = client.analyze_syntax(document=document)

    fmts = "{:10}: {}"
    print(fmts.format("sentences", len(response.sentences)))
    print(fmts.format("tokens", len(response.tokens)))
    for token in response.tokens:
        print(fmts.format(token.part_of_speech.tag.name, token.text.content))


if __name__ == "__main__":
    d = analyze_text_syntax("""BizDirect Asia is largest B2B contacts and companies data portal in Asia encompassed more than 17 millions companies and 50 millions business contacts across 1,000+ industries in 16 countries in Asia. Updated in real-time by our proprietary AI-powered system.Inside BizDirectAsia's platform are a network of AI and NLP algorithms to identify, verify and update information of a particular company, weed out inaccurate data and continuously refresh our data. It’s a platform that delivers Targeting Intelligence to address a range of business needs creating a single view of the market.""")
    import ipdb; ipdb.set_trace()