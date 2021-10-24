from torch.utils.data import Dataset
import pandas as pd
import torch


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
