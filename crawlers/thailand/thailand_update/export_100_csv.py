import pandas as pd
import json
import os

folder = 'data/'
names = os.listdir(folder)

registration_tax = []
amount = []
change = []
year = []
for name in names[:100]:
    data = json.load(open(folder+name))
    for d in data['total_revenue']:
        registration_tax.append(data['registration_tax'])
        amount_ = str(d['amount'])
        amount.append(amount_)
        change.append(str(d['%change']))
        year.append(d['year'])

df = pd.DataFrame({'registration_tax':registration_tax,'amount':amount,'%change':change,'year':year})
df.to_csv('100_company_update_thailand.csv', index=False)

