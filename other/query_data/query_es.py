import requests
import json
import pandas as pd

headers = {
    'Authorization': 'Basic YWJyYWhhbTpwQGliVmVIJSVUQlkwdHA3V3NCcGJ6eWE2',
    'Content-Type': 'application/json',
    'cache-control': 'no-cache',
}

all_data = []
size = 1000
index_ = 0
while True:
    query_body = {
        '_source': [
            'company_name',
            'id',
            'company_key',
            'province_name',
            'province_id',
            'founded_year',
            'revenue',
            'country_name',
            'country_code',
            'company_naics',
        ],
        'from': index_,
        'size': size,
        'query': {'bool': {'must': [{'range': {'revenue': {'gte': 0}}}]}}
    }

    response = requests.post('http://esbk.bizdirectasia.com/companies/_search', headers=headers, data=json.dumps(query_body))
    response = json.loads(response.text)
    try:
        length_res = len(response['hits']['hits'])
    except:
        break
    for i in range(length_res):
        exam = response['hits']['hits'][i]['_source']
        all_data.append(exam)
    
    print(index_/size)
    index_ += size
    if length_res < size or index_/size > 1000:
        break

df = pd.DataFrame(all_data)
df.to_csv('data_revenue_for_training_biz.csv', index=False)