import socket 
from geolite2 import geolite2 
import pycountry
import pandas as pd
from fuzzywuzzy import process, fuzz
from Levenshtein import distance as levenshtein_distance
import string
import re
from tqdm import tqdm


DCT_ISO_COUNTRY = {} 
for x in pycountry.countries: 
    DCT_ISO_COUNTRY[x.alpha_2] = x.name 

 
def get_country_from_domain(domain_str):
    dct_dot = {
        'vn': 'Vietnam',
        'bn': 'Brunei',
        'th': 'Thailand',
        'au': 'Australia',
        'jp': 'Japan',
        'kh': 'Cambodia',
        'nz': 'New Zealand',
        'la': 'Laos',
        'mm': 'Myanmar',
        'my': 'Malaysia',
        'id': 'Indonesia',
        'ph': 'Philippines',
        'hk': 'Hong Kong',
        'kr': 'South Korea',
        'tw': 'Taiwan',
        'sg': 'Singapore'
    }
    check = dct_dot.get(str(domain_str).split('.')[-1], '')
    if check != '':
        return check
    try:
        ip = socket.gethostbyname(domain_str.strip()) 
        reader = geolite2.reader()       
        output = reader.get(ip) 
        result = output['country']['iso_code']
        return DCT_ISO_COUNTRY[result]
    except:
        return "Unknown"

def preprocess(text):
    text = str(text).lower()
    text = re.sub(r'[^\x00-\x7F]+','', text)
    return text

def similariry_string(s1, s2):
    s1 = preprocess(s1)
    s2 = preprocess(s2)

    # fuz_score = fuzz.token_sort_ratio(s1, s2)/100
    fuz_score = fuzz.token_set_ratio(s1, s2)/100
    try:
        lev_score = (1-levenshtein_distance(s1, s2)/max(len(s1), len(s2)))
    except:
        lev_score = 0

    # print(f"s1: {s1}, s2: {s2}, fuz_score: {fuz_score:2f}, lev_score: {lev_score:2f}")
    return (fuz_score + lev_score)/2


def similar(company_name, clearbit_name, clearbit_domain):
    clearbit_domain = str(clearbit_domain).lower().split('.')
    clearbit_domain = ' '.join(clearbit_domain[:-1])
    
    score_name = similariry_string(company_name, clearbit_name)
    score_domain = similariry_string(company_name, clearbit_domain)

    # print(f"score similar name: {score_name:.2f}, score similar name with domain: {score_domain:2f}")
    return (score_name + score_domain)/2


def main(threshold=0.6):
    df = pd.read_csv("data_for_name_matching_sql.csv")
    select_cols = ['id', 'company_name', 'company_key', 'country', 'name_call_clearbit', 'name_tu_clearbit', 'domain', 'result_extract']
    df = df[select_cols]

    country_domain, confidence = [], []
    for i,row in tqdm(df.iterrows(), total=len(df)):
        company_name = row["name_call_clearbit"]
        clearbit_name = row["name_tu_clearbit"]
        clearbit_domain = row["domain"]

        country_domain.append(get_country_from_domain(clearbit_domain))
        switch_country = {
            "Viet Nam": "Vietnam",
            "Brunei Darussalam": "Brunei",
            "Lao People's Democratic Republic": "Laos",
            "Taiwan, Province of China": "Taiwan",
            "Korea, Republic of": "South Korea"
        }
        country_domain[-1] = switch_country.get(country_domain[-1], country_domain[-1])
        if similariry_string(country_domain[-1], row["country"]) != 1:
            confidence.append(.0)
        else:
            score = similar(company_name, clearbit_name, clearbit_domain)
            confidence.append(score)
            
    df["country_domain"] = country_domain
    df["confidence"] = confidence
    df["verified"] = df["confidence"].values > threshold
    df = df.rename(columns={
        "name_call_clearbit": "tradestyle",
        "name_tu_clearbit": "clearbit_name"
        })
    
    df.to_csv("result_verify_domain.csv", index=False)

    for i in range(5, 11):
        threshold = 0.1*i
        num_verified = sum(df["confidence"].values > threshold)
        percent = num_verified/df.shape[0]
        print(f"threshold: {threshold:1f}, verified: {num_verified}/{df.shape[0]}, percent: {percent*100:4f}%")

if __name__ == "__main__":
    main()