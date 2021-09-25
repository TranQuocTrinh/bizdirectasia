# coding: utf-8
import requests
import json

item = {
    "lst_keywords": [
        "golf school operation, golf equipment sales, golf practice course operation",
        "land for sale, land use consultation, new chikuhouse for sale, soundproof construction"
    ]
}

r = requests.post(url='http://127.0.0.1:6565/keywords2description', json=item)
print(r.content)
# print(json.loads(r.content))
