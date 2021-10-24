import sys
import time
from datetime import timedelta
import datetime

from pandas.core.frame import DataFrame
import torch
import pandas as pd
from tqdm import tqdm
from transformers import T5ForConditionalGeneration, T5Tokenizer
from torch.utils.data import DataLoader
import joblib
import json
import torch.nn as nn

from dataset import CustomDataset


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

    new_predictions = []
    for pred in predictions:
        split_pred = pred.split()
        if split_pred[0].strip() in {"wiki:", "wiki", ":"}:
            pred = " ".join(split_pred[1:])
        new_predictions.append(pred)
    return new_predictions


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input", help="which file data to use?", default=0)
    parser.add_argument("-d", "--device", help="which gpu to use?", default=0)
    parser.add_argument("-n", "--num_thread",
                        help="How many parts is the data divided?", default=1)
    parser.add_argument(
        "-t", "--thread", help="what part of the data?", default=0)
    args = parser.parse_args()

    device = torch.device("cuda:"+str(args.device)
                          if torch.cuda.is_available() else "cpu")

    class config:
        BATCH_SIZE = 16
        MAX_LEN = 128
        SUMMARY_LEN = 320
        MODEL_BASE = "t5-base"
        MODEL_PATH = "final_model/model_key2blog.pt"

    tokenizer = T5Tokenizer.from_pretrained(config.MODEL_BASE)

    model = T5ForConditionalGeneration.from_pretrained(config.MODEL_BASE)
    model.load_state_dict(torch.load(config.MODEL_PATH, map_location=device))
    model = model.to(device)

    print("Read file run mass...")
    start_time = time.time()

    #.sample(n=500).reset_index(drop=True)
    df = pd.read_csv("../wiki_data/version2/keyword.csv").reset_index(drop=True)

    number_samples = len(df)//int(args.num_thread)
    from_idx = number_samples * int(args.thread)
    if int(args.thread) == int(args.num_thread)-1:
        to_idx = len(df)
    else:
        to_idx = number_samples*(int(args.thread)+1)
    df = df[from_idx:to_idx].reset_index(drop=True)

    end_time = time.time()
    print("Time read file {}, number of company is {}, from_idx: {}, to_idx: {}".format(
        convert_seconds(end_time-start_time), len(df), from_idx, to_idx))

    test_set = CustomDataset(
        dataframe=df,
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

    lst_wiki = inference(
        tokenizer=tokenizer,
        model=model,
        loader=loader,
        device=device
    )
    from utils import clean_text
    df["wiki_clean"] = df.keyword.apply(clean_text)
    df["generate_wiki"] = lst_wiki
    df.to_csv(
        f"54k_generate_blog_{args.num_thread}_{args.thread}_{from_idx}_{to_idx}.csv", index=False)
    print("================================= DONE =========================================")


if __name__ == "__main__":
    main()
