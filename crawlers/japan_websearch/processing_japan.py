import pandas as pd
import json
import sys
import os
from tqdm import tqdm 

print('load file...')
df = pd.read_csv('jp-live-companies.csv')
dct_status = {
        1: 'New',
        11 :'Business name change',
        12 :'Domestic Location Change',
        13 :'Overseas Location Change',
        21 :'Registration Record Closure',
        22 :'Registration record resurrection',
        71 :'Merger',
        72 :'Absorption-type merger invalid',
        81 :'Registration of trade name Erasure',
        99 :'Delete'
        }
print('replace status by word..')
for i in tqdm(range(len(df))):
    df.iloc[i]['status'] = dct_status[df.iloc[i]['status']].lower()


common_word = ['国の機関','地方公共団体','株式会社','有限会社','合同会社','合名会社','合資会社']
print('remove common name...')
tradestyle = []
count = 0
for i in tqdm(range(len(df))):
    for c in common_word:
        x = df.iloc[i]['company_name'].replace(c,'')
    if x != df.iloc[i]['company_name']:
        count += 1
    tradestyle.append(x)

print(count)
df['tradestyle'] = tradestyle
df.to_csv('jp_process.csv',index=False)

df2 = pd.DataFrame({'company_id':df.company_id, 'tradestyle':tradestyle})
df2.to_csv('jp_use_translate_eng.csv', index=False)
#df2.to_excel(pd.ExcelWriter('translate.xlsx'))
