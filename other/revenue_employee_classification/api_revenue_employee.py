import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from flask import Flask, Response, jsonify, request
from flask import Request
import os
import json
import requests
import base64
import io
import ast
app = Flask(__name__)


class Model(nn.Module):
    def __init__(self, D_in=400, H1=256, H2=128, H3=3, D_out=5):
        super(Model, self).__init__()
        
        self.linear1 = nn.Linear(D_in, H1)
        self.linear2 = nn.Linear(H1, H2)
        self.linear3 = nn.Linear(H2, H3)
        self.linear4 = nn.Linear(H3+1, D_out)
        self.sofmax = nn.Softmax(dim=1)
        
    def forward(self, naics_code_vec, year):
        y_pred = self.linear1(naics_code_vec).clamp(min=0)
        y_pred = self.linear2(y_pred).clamp(min=0)
        y_pred = self.linear3(y_pred).clamp(min=0)
        y_pred = self.linear4(torch.cat([y_pred, year], dim=1))
        # y_pred = self.sofmax(y_pred)

        return y_pred


def inference(model, company_info, task='empoloyee'):
    DCT = {"means": {"founded_year": 2008.5482218110803}, "maxs": {"founded_year": 2018.0}, "mins": {"founded_year": 1915.0}}
    naics_code = [t for t in ast.literal_eval(company_info['company_naics'])] # 1 < len(code) < 7
    naics_code_len = [len(str(code)) - 2 for code in naics_code]
    naics_code_vec = torch.zeros(400)
    count = 0
    for i, (current_len, code) in enumerate(zip(naics_code_len, naics_code)):
        if i != 0 and current_len == naics_code_len[i-1]:
            count += 1
        else:
            count = 0
        try:
            naics_code_vec[current_len*80+count] = int(code)/10**(len(str(code)))
        except:
            count = 0

    year = (company_info['founded_year'] - DCT['means']['founded_year']) / (DCT['maxs']['founded_year']-DCT['mins']['founded_year'])
    
    naics_code_vec, year = torch.FloatTensor(naics_code_vec), torch.FloatTensor([year])
    naics_code_vec, year = naics_code_vec.unsqueeze(0).to(device), year.unsqueeze(0).to(device)

    pred =  model(naics_code_vec, year)
    pred = pred.cpu().detach()
    sofmax = nn.Softmax(dim=1)
    pred = sofmax(pred)
    y_pred = torch.argmax(pred).item()
    
    return y_pred


def reverse_class_revenue(class_):
    if class_ == 0:
        return '< 1M'       # 83,39%
    elif class_ == 1:
        return '1M - 5M'    # 10,79%
    elif class_ == 2:
        return '5M - 10M'   # 2,33%
    elif class_ == 3:
        return '10M - 100M' # 3,06%
    elif class_ == 4:
        return '> 100M'     # 0.40%
    

def reverse_class_employee(class_):
    if class_ == 0:
        return '<= 100'       # 83,39%
    elif class_ == 1:
        return '100 - 300'    # 10,79%
    elif class_ == 2:
        return '300 - 500'   # 2,33%
    elif class_ == 3:
        return '500 - 700' # 3,06%
    elif class_ == 4:
        return '> 700'     # 0.40%




@app.route('/revenue_employee_classification', methods=['POST'])
def revenue_employee_classification():
    try:
        company_info = {}
        company_info['company_naics'] = str(request.form['company_naics'])
        company_info['founded_year'] = float(request.form['founded_year'])
        
        revenue = inference(model_revenue, company_info, task='revenue')
        employee = inference(model_revenue, company_info, task='employee')

        rep = {'revenue': reverse_class_revenue(revenue), 'employee': reverse_class_employee(employee)}
        print(rep)
        return jsonify(rep)
    except Exception as e:
        return jsonify({'revenue': '', 'employee': '', 'error':e})
    

if __name__ == "__main__":
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    
    model_revenue = Model()
    model_revenue = model_revenue.to(device)
    model_revenue.load_state_dict(torch.load('model_revenue_classification.pt'))
    model_revenue.eval()

    model_employee = Model()
    model_employee = model_employee.to(device)
    model_employee.load_state_dict(torch.load('model_employee_classification.pt'))
    model_employee.eval()

    app.run("0.0.0.0", port=5022, debug=True)
