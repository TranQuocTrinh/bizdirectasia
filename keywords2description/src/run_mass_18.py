import sys
import time
from datetime import timedelta
import datetime
import torch
import pandas as pd
from tqdm import tqdm
from transformers import T5ForConditionalGeneration, T5Tokenizer
from torch.utils.data import DataLoader
import joblib
import json
import torch.nn as nn

from datasets import CustomDataset


def convert_seconds(seconds):
    sec = timedelta(seconds=seconds)
    d = datetime.datetime(1, 1, 1) + sec
    str_format = "%d days, %d hours, %d minutes, %d seconds" % (
        d.day-1, d.hour, d.minute, d.second)
    return str_format


def inference(tokenizer, model, loader, device):
    model.eval()
    predictions = []
    with torch.no_grad():
        bar = tqdm(enumerate(loader, 0), total=len(loader))
        for _, data in bar:
            ids = data["source_ids"].to(device, dtype=torch.long)
            mask = data["source_mask"].to(device, dtype=torch.long)

            generated_ids = model.generate(
                input_ids=ids,
                attention_mask=mask,
                max_length=320,
                num_beams=2,
                repetition_penalty=2.5,
                length_penalty=1.0,
                early_stopping=True
            )
            preds = [tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=True)
                     for g in generated_ids]
            predictions.extend(preds)

    predictions = [' '.join(p.split())
                   if p.split()[0].strip() != ':'
                   else ' '.join(p.split()[1:])
                   for p in predictions]
    return predictions


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input", help="which file dataa to use?", default=0)
    parser.add_argument("-d", "--device", help="which gpu to use?", default=0)
    parser.add_argument("-n", "--num_thread",
                        help="How many parts is the data divided?", default=4)
    parser.add_argument(
        "-t", "--thread", help="what part of the data?", default=0)
    args = parser.parse_args()

    device = torch.device("cuda:"+str(args.device)
                          if torch.cuda.is_available() else "cpu")

    print(f"Loading model on GPU {args.device}...")

    class config:
        BATCH_SIZE = 64
        MAX_LEN = 128
        SUMMARY_LEN = 320
        MODEL_BASE = "t5-base"
        MODEL_PATH = "final_model/epoch_95_model_t5-base_key2des.pt"

    tokenizer = T5Tokenizer.from_pretrained(config.MODEL_BASE)

    model = T5ForConditionalGeneration.from_pretrained(config.MODEL_BASE)
    model.load_state_dict(torch.load(config.MODEL_PATH, map_location=device))
    model = model.to(device)

    print("Read file run mass...")
    start_time = time.time()

    # result_extract_keywords = joblib.load(
    #     "/home/ubuntu/tqtrinh/description2keywords/18tr_companies/18mil_companies_extracted_keywords.joblib")

    path_file = f"18mil_companies/split/18tr_{args.input}.json"
    print("File use:", path_file)
    result_extract_keywords = json.load(open(path_file))

    number_samples = len(result_extract_keywords)//int(args.num_thread)
    from_idx = number_samples * int(args.thread)
    if int(args.thread) == int(args.num_thread)-1:
        to_idx = len(result_extract_keywords)
    else:
        to_idx = number_samples*(int(args.thread)+1)
    result_extract_keywords = result_extract_keywords[from_idx:to_idx]

    end_time = time.time()
    print("Time read file {}, number of company is {}".format(
        convert_seconds(end_time-start_time), len(result_extract_keywords)))
    print(f"Index from {from_idx} to {to_idx}")

    lst_keywords = [', '.join(d["keywords_generate"])
                    for d in tqdm(result_extract_keywords, desc="Prepare list of keywords")]

    test_dataset = pd.DataFrame({
        "keywords": ["keywords: " + keywords for keywords in lst_keywords]
    })

    test_set = CustomDataset(
        dataframe=test_dataset,
        tokenizer=tokenizer,
        source_len=config.MAX_LEN,
        summ_len=config.SUMMARY_LEN,
        phase="test",
    )

    loader = DataLoader(
        test_set,
        batch_size=config.BATCH_SIZE,
        shuffle=False,
        num_workers=0
    )

    lst_des = inference(
        tokenizer=tokenizer,
        model=model,
        loader=loader,
        device=device
    )
    for i in tqdm(range(len(result_extract_keywords)), desc="Final step!"):
        result_extract_keywords[i]["description_generate"] = lst_des[i]

    joblib.dump(result_extract_keywords,
                f"18mil_companies/18mi_companies_result_des2key_key2des_8-{args.input}-{args.num_thread}-{args.thread}.joblib")
    json.dump(result_extract_keywords, open(
        f"18mil_companies/18mi_companies_result_des2key_key2des_8-{args.input}-{args.num_thread}-{args.thread}.json", "w"))
    print("=============================================================================")


if __name__ == "__main__":
    main()
