import torch
import pandas as pd
from tqdm import tqdm
from transformers import T5ForConditionalGeneration, T5Tokenizer
from torch.utils.data import DataLoader

from datasets import CustomDataset

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from fastapi.responses import JSONResponse

app = FastAPI()


def inference(tokenizer, model, lst_keywords, config, device):
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

    predictions = [" ".join(p.split())
                   if p.split()[0].strip() not in {":", "description", "description:"}
                   else " ".join(p.split()[1:])
                   for p in predictions]
    return predictions


class Feature(BaseModel):
    lst_keywords: list


@app.get("/")
async def home():
    return "This is home page!"


@app.post("/keywords2description")
async def keywords2description(item: Feature):
    try:
        lst_des = inference(
            tokenizer=tokenizer,
            model=model,
            lst_keywords=item.lst_keywords,
            config=config,
            device=device
        )
        result = {
            "result": [
                {"keywords": ks, "description": d} for ks,d in zip(item.lst_keywords, lst_des)
            ],
            "status": "OK"
        }
    except Exception as e:
        result = {
            "result": [],
            "status": "ERROR - "+str(e),
        }
    return JSONResponse(result)


if __name__ == "__main__":
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print("Loading model...")

    class config:
        BATCH_SIZE = 1
        MAX_LEN = 128
        SUMMARY_LEN = 320
        MODEL_BASE = "t5-base"
        MODEL_PATH = "final_model/epoch_95_model_t5-base_key2des.pt"
    if device == torch.device("cpu"):
        print("Use CPU for inference...")
    else:
        config.BATCH_SIZE = 8
        print("Use GPU for inference...")

    tokenizer = T5Tokenizer.from_pretrained(config.MODEL_BASE)

    model = T5ForConditionalGeneration.from_pretrained(config.MODEL_BASE)
    model.to(device)
    model.load_state_dict(torch.load(config.MODEL_PATH, map_location=device))

    model.eval()

    uvicorn.run(app, host="0.0.0.0", port=6565)
