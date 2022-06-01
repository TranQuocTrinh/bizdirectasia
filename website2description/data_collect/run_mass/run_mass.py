import pandas as pd
import os
from tqdm import tqdm

import torch
from transformers import (
    LEDForConditionalGeneration,
    LEDTokenizer,
)

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


def main():
    import argparse
    parser = argparse.ArgumentParser()
    # Input
    parser.add_argument("--model_path", type=str, default=None, help="Path to model.")
    parser.add_argument("--path_df", type=str, default="content/singapore_content.csv", help="Path to run mass.")
    parser.add_argument("--max_source_length", default=2048, type=int, help="Maximum length of the source sequence")
    parser.add_argument("--max_target_length", default=128, type=int, help="Maximum length of the target sequence")
    parser.add_argument("--device", default="cuda", type=str, help="Device to use")
    args = parser.parse_args()

    # Load model, tokenizer
    tokenizer = LEDTokenizer.from_pretrained(args.model_path)
    model = LEDForConditionalGeneration.from_pretrained(args.model_path)
    model.eval()
    
    devive = torch.device("cuda" if torch.cuda.is_available() and args.device == "cuda" else "cpu")
    print("Model to device:", devive)
    model.to(devive)

    df = pd.read_csv(args.path_df)
    generations = []
    genornot = []
    for i,r in tqdm(df.iterrows(), total=len(df), desc="Generating"):
        if str(r["content"]).lower().strip() in {"nan", "", "unknown", "none"} or r["language"] in {"", "unknown", "none"}:
            generations.append("")
            genornot.append(False)
        else:
            input_text = preprocess_text(str(r['content']))
            if len(input_text) == 0:
                generations.append("")
                genornot.append(False)
            else:
                with torch.no_grad():
                    # Tokenize
                    inputs = tokenizer(
                        input_text, 
                        max_length=args.max_source_length, 
                        padding="max_length", 
                        truncation=True, 
                        return_tensors="pt"
                    )
                    if len(inputs["input_ids"][0]) <= 50:
                        generations.append(input_text)
                        genornot.append(False)
                    else:
                        # To device
                        inputs = {k: v.to(devive) for k, v in inputs.items()}
                        # Inference
                        output = model.generate(
                            **inputs, 
                            max_length=args.max_target_length, 
                            temperature=0.8, 
                            no_repeat_ngram_size=4,
                            do_sample=True,
                            early_stopping=True,
                            num_return_sequences=1,
                            min_length=50,
                        )
                        # Decode
                        desc = tokenizer.decode(output[0], skip_special_tokens=True)
                        desc = desc.strip().split("\n")[0]
                        desc = ".".join(desc.split(".")[:-1])+"."
                        generations.append(desc)
                        genornot.append(True)

    df["description_generated"] = generations
    df["gen_or_not"] = genornot
    out_path = os.path.join(os.path.dirname(args.path_df), "singapore_content_generated.csv")
    df.to_csv(out_path, index=False)


if __name__ == "__main__":
    main()