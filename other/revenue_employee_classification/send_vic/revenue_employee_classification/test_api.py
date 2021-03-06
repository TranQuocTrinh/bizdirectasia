# coding: utf-8
import requests 
import base64
import json

data = {"company_naics": """[23, 31, 32, 33, 44, 45, 51, 52, 54, 56, 81, 238, 313, 314, 315, 322, 323, 324, 325, 326, 327, 331, 332, 333, 337, 444, 453, 511, 512, 518, 519, 522, 541, 561, 812, 2383, 3133, 3149, 3152, 3159, 3222, 3231, 3241, 3259, 3261, 3279, 3312, 3313, 3327, 3333, 3371, 3372, 4441, 4532, 4539, 5111, 5121, 5182, 5191, 5222, 5414, 5416, 5418, 5419, 5614, 5619, 8129, 23834, 31331, 31491, 31524, 31599, 32221, 32222, 32223, 32311, 32412, 32591, 32611, 32799, 33122, 33131, 33272, 33331, 33711, 33721, 44412, 45322, 45392, 51119, 51212, 51219, 51821, 51919, 52221, 54141, 54142, 54143, 54149, 54161, 54181, 54185, 54189, 54192, 56143, 56191, 81299, 238340, 313310, 314910, 315240, 315990, 322219, 322220, 322230, 323111, 323113, 324122, 325910, 326112, 326113, 327999, 331221, 331315, 331318, 332721, 333316, 337110, 337212, 444120, 453220, 453920, 511191, 512120, 512199, 518210, 519190, 522210, 541410, 541420, 541430, 541490, 541613, 541614, 541810, 541850, 541890, 541921, 561439, 561910, 812990]""", "founded_year": 1986}

r = requests.post(url = 'http://127.0.0.1:5022/revenue_employee_classification', data=data)
r = json.loads(r.content)
print(json.dumps(r, indent=4))
