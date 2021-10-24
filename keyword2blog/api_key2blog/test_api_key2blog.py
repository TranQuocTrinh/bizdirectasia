# coding: utf-8
import requests
import json

item = {
    "lst_keyword": [
        "school",
        "software",
        "soundproof construction"
    ]
}

r = requests.post(url='http://127.0.0.1:6666/keywords2blog', json=item)
# print(r.content)
print(json.dumps(json.loads(r.content), indent=4))
