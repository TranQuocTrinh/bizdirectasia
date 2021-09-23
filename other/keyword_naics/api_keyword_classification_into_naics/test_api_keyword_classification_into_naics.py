# coding: utf-8
import requests
import json

item = {
    "lst_keyword": ['peanut wholesale', 'peanut sale'],
}

r = requests.post(
    url='http://127.0.0.1:3596/keyword_classification_into_naics',
    json=item
)
print(r.content)
# print(json.loads(r.content))
