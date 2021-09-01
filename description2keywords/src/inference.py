
import torch
from tqdm import tqdm
import pandas as pd
import json
import os
import joblib
import torch.nn.functional as F

from models import Model
from datasets import DES2KEYDataset
from utils import config

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


def inference(model, lst_text, mlb, threshold=0.5, k=5):
    df = pd.DataFrame({"description": lst_text})
    dataset = DES2KEYDataset(df, mlb, "test")
    lst_y_pred = []
    for i in tqdm(range(len(lst_text))):
        tokens_text = dataset[i].unsqueeze(0)
        tokens_text = tokens_text.to(device)

        output = model(tokens_text)
        output = output.cpu().detach()

        y_pred = mlb.inverse_transform(output > threshold)[0]
        y_pred = list(y_pred)
        if len(y_pred) < k:  # == 0:
            indices = torch.topk(output, k).indices
            new_indices = torch.zeros_like(output)
            new_indices[:, indices] = 1
            y_pred = mlb.inverse_transform(new_indices)[0]
            y_pred = list(y_pred)
        lst_y_pred.append(y_pred)
    return lst_y_pred


def inference_test_data(model, mlb):
    df = pd.read_csv(config["test_df_path"])
    keywords_pred, keywords_label_format, num_keywords, scores = [], [], [], []
    dfdataset = DES2KEYDataset(df=df, mlb=mlb)
    bar = tqdm(range(len(dfdataset)))
    for i in bar:

        tokens_text = dfdataset[i][0]
        tokens_text = tokens_text.to(device)
        tokens_text = tokens_text.unsqueeze(0)
        output = model(tokens_text)
        output = output.cpu().detach()

        threshold, k = 0.5, 5
        y_pred = mlb.inverse_transform(output > threshold)[0]
        y_pred = list(y_pred)
        if len(y_pred) < k:  # == 0:
            indices = torch.topk(output, k).indices
            new_indices = torch.zeros_like(output)
            new_indices[:, indices] = 1
            y_pred = mlb.inverse_transform(new_indices)[0]
            y_pred = list(y_pred)

        bar.set_postfix(threshold=threshold, len=len(y_pred))
        keywords_pred.append(y_pred)

        y_label = dfdataset[i][1].clone().detach().unsqueeze(0)
        y_label = mlb.inverse_transform(y_label)[0]
        y_label = list(y_label)
        keywords_label_format.append(y_label)
        num = f"{len(y_label)}-{len(y_pred)}-{len(set(y_label) & set(y_pred))}"
        num_keywords.append(num)
        scores.append(len(set(y_label) & set(y_pred)) /
                      min(len(y_label), len(y_pred)))

    df["keywords_pred"] = keywords_pred
    df["keywords"] = keywords_label_format
    df["num_keywords"] = num_keywords
    df["score"] = scores
    print(f"Score: {sum(scores)}")
    df.to_csv(f"{len(df)}_test_pred_samples.csv", index=False)


def main():
    mlb = joblib.load(config["encoder_label"])

    model = Model(num_classes=len(mlb.classes_))
    model.to(device)
    model.load_state_dict(torch.load(config["model_path"]))
    model.eval()

    lst_text = ["""
    BizDirect Asia is Southeast Asia’s largest COMPANY AND CONTACTS DATA platform, millions records of companies and contacts ACROSS ASEAN COUNTRIES BizDirect Asia is Asia's largest company data platform with more than 2.5 millions companies and 2 millions contact records spreading across 10 ASEAN countries (i.e. Vietnam, Thailand, Singapore, Malaysia, Indonesia, Philippines, Myanmar, Cambodia, Laos and Brunei). The platform is used mainly by B2B companies as a prospecting tool to search for new corporate customers by filtering by companies' sectors, locations, revenue size, employees counts, and many advanced search features such as nationality of shareholders, directors, etc.
    """, """Novaland Group is a reputable company in the field of Real Estate Investment and Development with more than 40 projects that have been developing in Vietnam today."""]
    lst_keywords_generate = inference(model, lst_text, mlb, k=5)
    for text, keywords in zip(lst_text, lst_keywords_generate):
        print(text)
        print(keywords)
        print("_"*50)

    input_df_path = "../sample_200_vietsing.csv"
    output_df_path = "../sample_200_vietsing_des2key.csv"
    df = pd.read_csv(input_df_path)
    df["keywords_generate"] = inference(
        model, list(df.description.values), mlb)
    df.to_csv(output_df_path, index=False)


if __name__ == "__main__":
    main()
