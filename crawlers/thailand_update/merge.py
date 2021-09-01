import pandas as pd
import os
from tqdm import tqdm
import json
import sys


names = os.listdir(sys.argv[1])

keys = ['company_key', 'company_id', 'business_id', 'company_name', 'juristic_name', 'status', 'registered_date', 
        'registered_capital', 'last_registered_id', 'address', 'tel', 'fax', 'website', 'e-mail_address', 
        'industry_group_doc', 'industry_group_last', 'director_1', 'director_2', 'director_3', 'director_4', 
        'director_5', 'partner_1', 'partner_2', 'partner_3', 'partner_4', 'partner_5', 'total_revenue_2017', 
        'total_revenue_2018', 'total_revenue_2019', 'net_profit_loss_2017', 'net_profit_loss_2018', 'net_profit_loss_2019']
df = {key:[] for key in keys}
error = []
for name in tqdm(names):
    try:
        data = json.load(open(sys.argv[1]+name))
    except:
        error.append(name)
        continue

    for k in list(df.keys()):
        try:
            df[k].append(data[k])
        except:
            df[k].append('')

print('Len error: ', len(error))
df = pd.DataFrame(df)
df.to_csv('sample_data_thai_update.csv', index=False)
