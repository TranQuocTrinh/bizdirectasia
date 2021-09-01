import json
import pandas as pd
import os
import sys 
from tqdm import tqdm

df = pd.read_csv('data_vietnam_registration.csv')

path = sys.argv[1]
names = os.listdir(path)
count = 0
for name in tqdm(names):
    row = json.load(open(path+name))
    #print(row.keys())
    registration_tax = str(df.registration_tax[row['index']]).lower()
    #print(df.iloc[row['index']])
    #print('\n\n\n')
    if registration_tax == row['registration_tax'] or registration_tax == 'nan':
        df.registration_tax[row['index']] = row['registration_tax']
        if row['director_names'] != '':
            df.director_names[row['index']] = row['director_names']
        try:
            if row['founded_address'] != '':
                df.founded_address[row['index']] = row['founded_address']
        except:
            if row['founded_addresss'] != '':
                df.founded_address[row['index']] = row['founded_addresss']
        try:
            if row['founded_year'] != '':
                df.founded_year[row['index']] = row['founded_year']
        except:
            print(row)
        count += 1
    #print(df.iloc[row['index']])

print('Number row fill:', count)
df.to_csv('data_vietnam_registration_fill.csv')
