# coding: utf-8
import requests
import json

item = {
    "lst_company_name": ["Yoshimi Co., Ltd.", "Suzuki Kashichi Shoten Co., Ltd"],
    "lst_description": ["Mainly engaged in construction management of sign work, painting work, and other building repair work at gas stations. He also conducts carpentry work, plastering, and earthwork.", "Manufactures soap and detergents in Nagoya City, Aichi Prefecture."],
    "mink": 10,      # default 5
    "maxk": 15      # default 20
}

r = requests.post(url='http://127.0.0.1:2357/description2keywords', json=item)
print(r.content)
# print(json.loads(r.content))
