import torch
import joblib
import pandas as pd
from models import Model
from utils import config
import torch.nn as nn
from tqdm import tqdm
from transformers import BertTokenizer
from datasets import DES2KEYDataset

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from fastapi.responses import JSONResponse

app = FastAPI()


def inference(model, lst_company_name, lst_description, mlb, tokenizer, threshold=0.4, mink=5, maxk=20, device=torch.device("cpu")):
    df = pd.DataFrame({"company_name": lst_company_name,
                      "description": lst_description})

    dataset = DES2KEYDataset(
        df=df, mlb=mlb, tokenizer=tokenizer, phase="test")

    lst_y_pred = []
    with torch.no_grad():
        for i in tqdm(range(df.shape[0])):
            des_ids = dataset[i].unsqueeze(0)
            des_ids = des_ids.to(device)

            output = model(des_ids)

            output = output.cpu().detach()

            y_pred = mlb.inverse_transform(output > threshold)[0]
            y_pred = list(y_pred)
            if len(y_pred) > maxk:
                indices = torch.topk(output, maxk).indices
                new_indices = torch.zeros_like(output)
                new_indices[:, indices] = 1
                y_pred = mlb.inverse_transform(new_indices)[0]
                y_pred = list(y_pred)

            elif len(y_pred) < mink:
                indices = torch.topk(output, mink).indices
                new_indices = torch.zeros_like(output)
                new_indices[:, indices] = 1
                y_pred = mlb.inverse_transform(new_indices)[0]
                y_pred = list(y_pred)

            lst_y_pred.append(y_pred)
    return lst_y_pred


class Feature(BaseModel):
    lst_company_name: list
    lst_description: list
    mink: int = 5
    maxk: int = 20


@app.get("/")
async def home():
    return "This is home page!"


@app.post("/description2keywords")
async def description2keywords(item: Feature):
    print(item)
    result = inference(
        model=model,
        lst_company_name=item.lst_company_name,
        lst_description=item.lst_description,
        mlb=mlb,
        tokenizer=tokenizer,
        mink=item.mink,
        maxk=item.maxk,
        device=device
    )
    return JSONResponse(result)


if __name__ == "__main__":
    device = torch.device("cuda:3" if torch.cuda.is_available() else "cpu")
    config = dict(
        model_base="bert-base-uncased",
        model_path="./final_model/model_BERT2ML_classification_name-add-des_300k.pt",
        encoder_label="./final_model/mlb_encoder_label_300k.joblib",
    )

    tokenizer = BertTokenizer.from_pretrained(config["model_base"])
    mlb = joblib.load(config["encoder_label"])

    model = Model(num_classes=len(mlb.classes_))
    model.load_state_dict(torch.load(
        config["model_path"], map_location=device))
    model.to(device)
    model.eval()

    uvicorn.run(app, host="0.0.0.0", port=2357)
