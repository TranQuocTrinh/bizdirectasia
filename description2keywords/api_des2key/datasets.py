import pandas as pd
import torch
import ast
from torch.utils.data import Dataset


class DES2KEYDataset(Dataset):
    def __init__(self, df, mlb, tokenizer, phase="train"):
        self.df = df
        self.mlb = mlb
        self.phase = phase
        self.tokenizer = tokenizer
        self.maxlen_encoder = 350

    def convert_line_uncased(self, text, maxlen):
        tokens_a = self.tokenizer.tokenize(text)[:maxlen]
        one_token = self.tokenizer.convert_tokens_to_ids(
            ["[CLS]"] + tokens_a + ["[SEP]"]
        )
        one_token += [0] * (maxlen - len(tokens_a))
        return one_token

    def __len__(self):
        return len(self.df)

    def __getitem__(self, index):
        description = str(self.df.loc[index, "description"])
        company_name = str(self.df.loc[index, "company_name"])

        des_tokens = self.convert_line_uncased(
            company_name + " " + description, maxlen=self.maxlen_encoder)
        input_ids = torch.LongTensor(des_tokens)
        if self.phase == "train":
            keywords = ast.literal_eval(self.df.loc[index, "keywords"])
            labels = self.mlb.transform([set(keywords)])[0]
            labels = torch.FloatTensor(labels)

            return input_ids, labels
        else:
            return input_ids
