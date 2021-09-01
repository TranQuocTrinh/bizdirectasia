import language_check
import sys
import os
from tqdm import tqdm
import pandas as pd

folder = sys.argv[1]
names = os.listdir(folder)
tool = language_check.LanguageTool('en-US')


for name in tqdm(names):
    short_description = []
    short_bug = []
    business_description = []
    business_bug = []

    df = pd.read_csv(folder+name)
    
    for i in tqdm(range(len(df))):
        if str(df.iloc[i]['short_description']).lower() == 'nan':
            short_description.append('')
            short_bug.append('[]')
        else:
            gram = tool.check(str(df.iloc[i]['short_description']))
            short_description.append(str(len(gram)))
            short_bug.append(str(gram))

        if str(df.iloc[i]['business_description']).lower() == 'nan':
            business_description.append('')
            business_bug.append('[]')
        else:
            gram = tool.check(str(df.iloc[i]['business_description']))
            business_description.append(str(len(gram)))
            business_bug.append(str(gram))

    df['grammar_check_short'] = short_description
    df['short_error'] = short_bug
    df['grammar_check_business'] = business_description
    df['business_error'] = business_bug
    df.to_csv('./data_checked/checked_bug_'+name, index=False)
