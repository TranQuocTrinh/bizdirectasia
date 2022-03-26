from bs4 import BeautifulSoup
import requests
import string
import re
from tqdm import tqdm
import json
import os
import pandas as pd


def get_content_from_url(url, output_dir=None, timeout=20, paragraph=False):
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

def load_model_tokenizer_fb():
    from transformers import pipeline, AutoTokenizer
    print("Load model summary...")
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
    print("Done loading model summary!")
    return summarizer, tokenizer

def summarize_fb(summarizer, text, min_length=100, max_length=150):
    return summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)[0]

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
    return response, result_dict


def get_noun_phrases(response):
    analyze = []
    for i, token in enumerate(response.tokens):
        analyze.append((token.part_of_speech.tag.name, token.text.content))
    noun_phrase_list = []
    current_idx = 0
    for i,token in enumerate(response.tokens):
        if token.part_of_speech.tag.name in {"NOUN"} and i >= current_idx:
            j = i + 1
            while j < len(response.tokens) and response.tokens[j].part_of_speech.tag.name == "NOUN" and response.tokens[j].text.content != ".":
                j += 1
            lst_noun = [token.text.content for token in response.tokens[i:j]]
            if len(lst_noun) > 1:
                noun_phrase_list.append(" ".join(lst_noun))
            current_idx = j

    return analyze, noun_phrase_list



from text_preprocessing import text_preprocessing


def main():
    df = []
    # url_list = ["https://bizdirectasia.com/", "https://stackoverflow.com/"]
    url_list = open("/home/ubuntu/tqtrinh/web2contact_matching/domain/networksdb.io-domains_sg.txt").read()
    url_list = [url for url in url_list.split("\n") if url != ""][0:1000]
    model_fb, tokenizer_fb = load_model_tokenizer_fb()
    # model, tokenizer = load_model_tokenizer("sshleifer/distilbart-cnn-12-6")
    get_content_time, extract_time = [], []
    import time
    bar = tqdm(enumerate(url_list), total=len(url_list))
    count = 0
    for i, url in bar:
        start = time.time()
        content = get_content_from_url(url, paragraph=True)
        content = text_preprocessing(str(content))
        get_content_time.append(time.time() - start)
        
        # summary = summarize(model, tokenizer, [text])[0]
        start = time.time()
        token_ids = tokenizer_fb.encode(content)[1:-1]
        content = tokenizer_fb.decode(token_ids[:1022])
        try:
            summary_or_not = "no_summary" if len(token_ids) < 150 else "summary"
            summary_fb = {"summary_text": content} if len(token_ids) < 150 else summarize_fb(model_fb, content)
        except:
            summary_fb = {"summary_text": content}
            summary_or_not = "no_summary"

        # try:
        res, _ = analyze_text_syntax(summary_fb["summary_text"])
        analyze, noun_phrase_list = get_noun_phrases(res)

        # except:
            # res, summary_fb, analyze, noun_phrase_list = {}, {"summary_text":""}, [], []
        extract_time.append(time.time() - start)
        row = {
            "website": url, 
            "content": content, 
            "summary": summary_fb["summary_text"], 
            "summary_or_not": summary_or_not, 
            "analyze": analyze, 
            "noun_phrase_list": noun_phrase_list
        }
        df.append(row)
        count += len(noun_phrase_list) > 0
        bar.set_description(f"Extracting... {count}/{len(url_list)}")
        bar.set_postfix(get_content_time=f"{sum(get_content_time)/len(get_content_time):.2f}", summurize_extract_time=f"{sum(extract_time)/len(extract_time):.2f}")
        pd.DataFrame(df).to_csv("100_urls_singapore_extract_keyword.csv", index=False)
    
    df = pd.DataFrame(df)
    print(df)
    df.to_csv("100_urls_singapore_extract_keyword.csv", index=False)

if __name__ == "__main__":
    main()