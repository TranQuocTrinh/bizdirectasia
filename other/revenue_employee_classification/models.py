import numpy as np
import pandas as pd
import os
import math
from PIL import Image
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


# class Model(nn.Module):
#     def __init__(self, D_in=400, H1=256, H2=128, H3=3, D_out=4):
#         super(Model, self).__init__()
        
#         self.linear1 = nn.Linear(D_in, H1)
#         self.linear2 = nn.Linear(H1, H2)
#         self.linear3 = nn.Linear(H2, H3)
#         self.linear4 = nn.Linear(H3+1+1, D_out)
#         self.sofmax = nn.Softmax(dim=1)
        
#     def forward(self, naics_code_vec, province_id, year):
#         y_pred = self.linear1(naics_code_vec).clamp(min=0)
#         y_pred = self.linear2(y_pred).clamp(min=0)
#         y_pred = self.linear3(y_pred).clamp(min=0)
#         y_pred = self.linear4(torch.cat([y_pred, province_id, year], dim=1))
#         y_pred = self.sofmax(y_pred)

#         return y_pred


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
