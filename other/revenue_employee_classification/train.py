from utils import *
from datasets import *
from models import *
import torch
import torch.nn as nn
from tqdm import tqdm
import torchvision.transforms as transforms
from collections import Counter
from torch import optim
import random
import os
import json
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_recall_fscore_support
from sklearn.metrics import accuracy_score

TASK = 'revenue'
CREATE_DATA_TRAIN = 0
SAMPLE_FRAC = 1
MODEL_PATH = f'model_{TASK}_classification.pt'
BATCH_SIZE = 128
N_EPOCHS = 120
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


def train(model, train_loader, criterion, optimizer):
    model.train()
    running_loss, correct, total = 0., 0, 0
    bar = tqdm(train_loader, total=len(train_loader))
    for naics_code_vec, year, target in bar:
        naics_code_vec, year, target = naics_code_vec.to(device), year.to(device), target.to(device)
        # zero the parameter gradients
        optimizer.zero_grad()
        # forward + backward + optimize
        outputs = model(naics_code_vec, year)
        loss = criterion(outputs, target)
        
        loss.backward()
        optimizer.step()
        # print statistics
        running_loss += loss.item()
        _, pred = torch.max(outputs, dim=1)
        correct += torch.sum(pred == target).item()
        total += target.size(0)

    # accuracy, recall, fscore, support = precision_recall_fscore_support(y_true, y_pred, average='micro')
    accuracy = correct/total
    loss_score = running_loss/len(train_loader)
    return accuracy, loss_score


def eval(model, val_loader, criterion, optimizer):
    model.eval()
    running_loss_v, correct, total = 0., 0, 0
    bar = tqdm(val_loader, total=len(val_loader))
    for naics_code_vec, year, target in bar:
        naics_code_vec, year, target = naics_code_vec.to(device), year.to(device), target.to(device)
        outputs = model(naics_code_vec, year)
        loss = criterion(outputs, target)
        running_loss_v += loss.item()
        _,pred_v = torch.max(outputs, dim=1)
        correct += torch.sum(pred_v == target).item()
        total += target.size(0)

    # accuracy, recall, fscore, support = precision_recall_fscore_support(y_true_v, y_pred_v, average='micro')
    accuracy = correct/total
    loss_score_v = running_loss_v/len(val_loader)
    return accuracy, loss_score_v

def preprocess_data(data, task='employee'):
    means, maxs, mins = dict(), dict(), dict()
    dct = {
        'means': {},
        'maxs': {},
        'mins': {}
    }
    select_cols = ['founded_year']
    for col in select_cols:
        dct['means'][col] = float(data[col].mean())
        dct['maxs'][col] = float(data[col].max())
        dct['mins'][col] = float(data[col].min())
    
    # data['province_id_nor'] = (data['province_id'].values - dct['means']['province_id']) / (dct['maxs']['province_id']-dct['mins']['province_id'])
    data['founded_year_nor'] = (data['founded_year'].values - dct['means']['founded_year']) / (dct['maxs']['founded_year']-dct['mins']['founded_year'])
    data['revenue_label'] = [revenue_class(x) for x in data['revenue'].values]
    data['employee_label'] = [employee_class(x) for x in data['staff_qty'].values]

    if task == 'revenue':
        count = Counter(data['revenue_label'].values)
        min_num_sam = min(count.values())*2
        idx = []
        count = {i:0 for i in range(5)}
        for i,row in data.iterrows():
            if count[row['revenue_label']] < min_num_sam:
                count[row['revenue_label']] += 1
                idx.append(i)
        data = data.loc[idx, ].reset_index(drop=True)

    train_df, val_df = train_test_split(data, test_size=0.1, random_state=42)
    train_df = train_df.reset_index(drop=True)
    val_df = val_df.reset_index(drop=True)
    print('Created training data!')
    print(data.shape)
    if task == 'revenue':
        count = Counter(data['revenue_label'].values)
    else:
        count = Counter(data['employee_label'].values)
    
    print(task)
    print(count)
    
    return train_df, val_df, dct


def main():
    if CREATE_DATA_TRAIN:
        data = pd.read_csv('../data/data_revenue_employee_all.csv')
        data = data[data.revenue != 0].reset_index(drop=True).sample(frac=SAMPLE_FRAC).reset_index(drop=True)

        train_df, val_df, dct = preprocess_data(data, task=TASK)
        json.dump(dct, open(f'mean_max_min_{TASK}.json','w'))

        train_df.to_csv(f'train_{TASK}.csv', index=False)
        val_df.to_csv(f'val_{TASK}.csv', index=False)
        
        exit()
    else:
        train_df = pd.read_csv(f"train_{TASK}.csv")
        val_df = pd.read_csv(f"val_{TASK}.csv")
        print(train_df)
        print(val_df)
        print('Train:', train_df.shape)
        print('Validation:', val_df.shape)

    train_dataset = RevenueDataset(data=train_df, task=TASK)
    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=4)

    val_dataset = RevenueDataset(data=val_df, task=TASK)
    val_loader = torch.utils.data.DataLoader(val_dataset, batch_size=BATCH_SIZE)

    model = Model()
    model.to(device)
    if os.path.exists(MODEL_PATH):
        model.load_state_dict(torch.load(MODEL_PATH))
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.0001)
    # optimizer = torch.optim.SGD(model.parameters(), lr=1e-2)

    real_val_acc = -np.Inf
    # real_loss = np.Inf

    for epoch in range(1, N_EPOCHS+1):
        print('\nEpoch = [{}]/[{}]\n'.format(epoch, N_EPOCHS))
        t_acc, t_loss = train(model, train_loader, criterion, optimizer)
        print(f'\ntrain loss: {t_loss:.4f}, train acc: {t_acc*100:.4f}')
        with torch.no_grad():
            v_acc, v_loss = eval(model, val_loader, criterion, optimizer)
            print(f'validation loss: {v_loss:.4f}, validation acc: {v_acc*100:.4f}\n')

            network_learned = v_acc > real_val_acc
            # network_learned = real_loss > v_loss
            # Saving the best weight
            if network_learned:
                real_val_acc = v_acc
                # real_loss = v_loss
                torch.save(model.state_dict(), MODEL_PATH)
                print('Detected network improvement, saving current model')

        print_screen = 'The current highest accuracy is {}%|'.format(round(real_val_acc*100,5))
        print('-'*len(print_screen) + '\n' + print_screen + '\n' + '-'*len(print_screen) + '\n')

if __name__ == "__main__":
    main()
