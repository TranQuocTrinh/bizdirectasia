from models import Model
import torch
import torch.nn as nn
import numpy as np
from tqdm import tqdm
import torchvision.transforms as transforms
import pandas as pd
from torch.utils.data import Dataset
import json
import ast
import os
import io
import joblib
import torch.nn.functional as F
from utils import *


device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# DCT_EM = json.load(open('mean_max_min_employee.json'))
# DCT_RE = json.load(open('mean_max_min_revenue.json'))

DCT = {"means": {"founded_year": 2008.5482218110803}, "maxs": {"founded_year": 2018.0}, "mins": {"founded_year": 1915.0}}

def inference(model, company_info, task='empoloyee'):
    naics_code = [t['naics_code'] for t in ast.literal_eval(company_info['company_naics'])] # 1 < len(code) < 7
    naics_code_len = [len(str(code)) - 2 for code in naics_code]
    naics_code_vec = torch.zeros(400)
    count = 0
    for i, (current_len, code) in enumerate(zip(naics_code_len, naics_code)):
        if i != 0 and current_len == naics_code_len[i-1]:
            count += 1
        else:
            count = 0
        naics_code_vec[current_len*80+count] = int(code)/10**(len(str(code)))

    # if task=='revenue':
    #     #year = company_info['founded_year_nor']
    #     year = (company_info['founded_year'] - DCT_RE['means']['founded_year']) / (DCT_RE['maxs']['founded_year']-DCT_RE['mins']['founded_year'])
    # else:
    #     year = (company_info['founded_year'] - DCT_EM['means']['founded_year']) / (DCT_EM['maxs']['founded_year']-DCT_EM['mins']['founded_year'])

    year = (company_info['founded_year'] - DCT['means']['founded_year']) / (DCT['maxs']['founded_year']-DCT['mins']['founded_year'])
    
    naics_code_vec, year = torch.FloatTensor(naics_code_vec), torch.FloatTensor([year])
    naics_code_vec, year = naics_code_vec.unsqueeze(0).to(device), year.unsqueeze(0).to(device)

    pred =  model(naics_code_vec, year)
    pred = pred.cpu().detach()
    sofmax = nn.Softmax(dim=1)
    pred = sofmax(pred)
    y_pred = torch.argmax(pred).item()
    
    return y_pred


def main():
    df = pd.read_csv('val_employee.csv')
    infer_samples = []
    model_revenue = Model()
    model_revenue.to(device)
    model_revenue.load_state_dict(torch.load('model_revenue_classification.pt'))
    model_revenue.eval()
    
    model_employee = Model()
    model_employee.to(device)
    model_employee.load_state_dict(torch.load('model_employee_classification.pt'))
    model_employee.eval()

    for i in range(100):
        company_info = {
            'company_naics': df.iloc[i]['company_naics'],
            'founded_year_nor': df.iloc[i]['founded_year_nor'],
            'founded_year': df.iloc[i]['founded_year'],
            'revenue': df.iloc[i]['revenue'],
            'staff_qty': df.iloc[i]['staff_qty'],
        }

        revenue_pred = inference(model_revenue, company_info)
        employee_pred = inference(model_employee, company_info)
        temp = {
            'company_key': df.iloc[i]['company_key'],
            'company_name': df.iloc[i]['company_name'],
            'country_name': df.iloc[i]['country_name'],
            'company_naics': df.iloc[i]['company_naics'],
            'founded_year': df.iloc[i]['founded_year'],
            'province_id': df.iloc[i]['province_id'],
            'revenue_real': reverse_class_revenue(df.iloc[i]['revenue_label']),
            'revenue_pred': reverse_class_revenue(revenue_pred),
            'employee_real': reverse_class_employee(df.iloc[i]['employee_label']),
            'employee_pred': reverse_class_employee(employee_pred),
        }
        infer_samples.append(temp)
    
    df = pd.DataFrame(infer_samples)
    select = ['revenue_real', 'revenue_pred', 'employee_real', 'employee_pred']
    print(df[select])
    df.to_csv('infer_samples.csv', index=False)
if __name__ == '__main__':
    main()
