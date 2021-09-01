# coding: utf-8
import requests 
import base64
import json

data = {"keyword": "data science"}
r = requests.post(url = 'http://127.0.0.1:2201/keyword_category', data = data)
print(r.content)