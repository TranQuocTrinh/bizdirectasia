import pandas as pd
import numpy as np
import os
import torch
import torch.nn as nn
from torch.utils.data import Dataset
import ast


class RevenueDataset(Dataset):
    def __init__(self, data, task='revenue'):
        self.data = data
        self.task = task

    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, index):
        try:
            naics_code = [t['naics_code'] for t in ast.literal_eval(self.data.loc[index, 'company_naics'])] # 1 < len(code) < 7
            naics_code_len = [len(str(code)) - 2 for code in naics_code]
            naics_code_vec = torch.zeros(400)
            count = 0
            for i, (current_len, code) in enumerate(zip(naics_code_len, naics_code)):
                if i != 0 and current_len == naics_code_len[i-1]:
                    count += 1
                else:
                    count = 0
                naics_code_vec[current_len*80+count] = int(code)/10**(len(str(code)))

            year = self.data.loc[index, 'founded_year_nor']

            # province_id = self.data.loc[index, 'province_id_nor']
            if self.task == 'revenue':
                label = self.data.loc[index, 'revenue_label']
            else:
                label = self.data.loc[index, 'employee_label']
        except:
            index = 0
            naics_code = [t['naics_code'] for t in ast.literal_eval(self.data.loc[index, 'company_naics'])] # 1 < len(code) < 7
            naics_code_len = [len(str(code)) - 2 for code in naics_code]
            naics_code_vec = torch.zeros(400)
            count = 0
            for i, (current_len, code) in enumerate(zip(naics_code_len, naics_code)):
                if i != 0 and current_len == naics_code_len[i-1]:
                    count += 1
                else:
                    count = 0
                naics_code_vec[current_len*80+count] = int(code)/10**(len(str(code)))

            year = self.data.loc[index, 'founded_year_nor']

            # province_id = self.data.loc[index, 'province_id_nor']
            if self.task == 'revenue':
                label = self.data.loc[index, 'revenue_label']
            else:
                label = self.data.loc[index, 'employee_label']

        return torch.FloatTensor(naics_code_vec), torch.FloatTensor([year]), torch.tensor(label, dtype=torch.long) #torch.LongTensor([label])
