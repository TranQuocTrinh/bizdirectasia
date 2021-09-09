# coding: utf-8
import requests
import base64
import json

item = {
    "lst_company_name": ["Yoshimi Co., Ltd.", "Suzuki Kashichi Shoten Co., Ltd"],
    "lst_description": ["Mainly engaged in construction management of sign work, painting work, and other building repair work at gas stations. He also conducts carpentry work, plastering, and earthwork.", "Manufactures soap and detergents in Nagoya City, Aichi Prefecture."]
}

r = requests.post(url='http://127.0.0.1:2357/description2keywords', json=item)
print(json.loads(r.content))
