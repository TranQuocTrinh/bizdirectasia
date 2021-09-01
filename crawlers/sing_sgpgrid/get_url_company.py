from tqdm import tqdm
import requests
import re
import json
import time

def extract_url(text):
    urls = []
    for a in text.split('<loc>'):
        urls.append(a.split('</loc>')[0])
    return urls

all_url = []
for i in tqdm(range(0, 35)):
    temp = extract_url(requests.get('https://sgpgrid.com/sitemap/Companies/sitemap-Companies-'+str(i)+'.xml').text)
    if len(temp) == 0:
        break
    else:
        all_url = all_url + temp
    print('len =', len(all_url))
    time.sleep(3)

print(len(all_url))
all_url = list(set(all_url))
print(len(all_url))
json.dump(all_url, open('urls.json','w'))
