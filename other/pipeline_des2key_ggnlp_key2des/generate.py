
from torch.utils.data import Dataset
import pandas as pd
import torch
from tqdm import tqdm
from transformers import T5ForConditionalGeneration, T5Tokenizer
from torch.utils.data import DataLoader


class CustomDataset(Dataset):

    def __init__(self, dataframe, tokenizer, source_len, summ_len, phase):
        self.tokenizer = tokenizer
        self.data = dataframe
        self.source_len = source_len
        self.summ_len = summ_len
        self.phase = phase
        if self.phase == "train":
            self.description = self.data.description
        self.keywords = self.data.keywords

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        keywords = str(self.keywords[index])
        keywords = " ".join(keywords.split())

        source = self.tokenizer.batch_encode_plus(
            [keywords],
            max_length=self.source_len,
            pad_to_max_length=True,
            truncation=True,
            padding="max_length",
            return_tensors="pt"
        )
        source_ids = source["input_ids"].squeeze()
        source_mask = source["attention_mask"].squeeze()

        if self.phase in {"train"}:
            description = str(self.description[index])
            description = " ".join(description.split())

            target = self.tokenizer.batch_encode_plus(
                [description],
                max_length=self.summ_len,
                pad_to_max_length=True,
                truncation=True,
                padding="max_length",
                return_tensors="pt"
            )

            target_ids = target["input_ids"].squeeze()
            target_mask = target["attention_mask"].squeeze()

            return {
                "source_ids": source_ids.to(dtype=torch.long),
                "source_mask": source_mask.to(dtype=torch.long),
                "target_ids": target_ids.to(dtype=torch.long),
                "target_mask": target_mask.to(dtype=torch.long)
            }
        elif self.phase in {"test"}:
            return {
                "source_ids": source_ids.to(dtype=torch.long),
                "source_mask": source_mask.to(dtype=torch.long),
            }


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


import pandas as pd
import json
from google.cloud import language_v1
from tqdm import tqdm


def get_keywords(response):
    try:
        response_json = json.loads(response)
    except:
        return ""

    keywords = []
    for x in response_json:
        if language_v1.Entity.Type(x["type"]).name in {"PERSON", "LOCATION", "ORGANIZATION", "CONSUMER_GOOD"}:
            keywords.append(x["name"])
    keywords = list(set(keywords))
    return ", ".join(keywords)




def main():
    df = pd.read_csv("10k_example_data_with_ggnlp.csv")
    df["keywords"] = [get_keywords(x) for x in tqdm(df["entities"])]

    # Load model
    class config:
        BATCH_SIZE = 32
        MAX_LEN = 128
        SUMMARY_LEN = 320
        MODEL_BASE = "t5-base"
        MODEL_PATH = "keyword-2-description-main/app/final_model/epoch_95_model_t5-base_key2des.pt"


    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = T5Tokenizer.from_pretrained(config.MODEL_BASE)
    model = T5ForConditionalGeneration.from_pretrained(config.MODEL_BASE)
    model.to(device)
    model.load_state_dict(torch.load(config.MODEL_PATH, map_location=device))
    model.eval() 

    df["gen_desc_new"] = ""
    df.loc[df["keywords"] !="", "gen_desc_new"] = inference(tokenizer, model, df[df["keywords"] !=""]["keywords"].values.tolist(), config, device)

    df.to_csv("10k_example_data_with_ggnlp_gen_desc.csv", index=False)
        

if __name__ == "__main__":
    main()