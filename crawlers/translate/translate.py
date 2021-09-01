import json
import time
from textblob import TextBlob

def translate_data(text, time_sleep=1.0):
#    try:
    n_blob = TextBlob(str(text))
    str_vn_back_translate = n_blob.translate(from_lang=n_blob.detect_language(), to='vi')
    time.sleep(time_sleep)
#    except:
#        print('None')
#        return None

    return str(str_vn_back_translate)

import pandas as pd
xl_file = pd.ExcelFile('baseconnect_Cat_keywords.xlsx')
dfs = {sheet_name: xl_file.parse(sheet_name) for sheet_name in xl_file.sheet_names}
df = dfs['Sheet1']

from tqdm import tqdm
category_name = [translate_data(x) for x in tqdm(df.category_name)]
keywords = [translate_data(x) for x in tqdm(df.keywords)]
characteristic = [translate_data(x) for x in tqdm(df.characteristic)]

df.category_name = category_name
df.keywords = keywords
df.characteristic = characteristic

df.to_csv('baseconnect_Cat_keywords_translate.csv')
