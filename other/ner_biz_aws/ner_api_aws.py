import boto3 
import json 
from langdetect import detect
import json
from tqdm import tqdm
import os
import pandas as pd



def main():
    comprehend = boto3.client(service_name='comprehend', region_name='us-east-2')

    if not os.path.exists('response_aws'):
        os.makedirs('response_aws')

    descriptions = json.load(open('descriptions.json'))

    countfile, i = 0, 0
    while countfile < 1000:
        desc = descriptions[i]
        i += 1
        if len(desc) > 20 and detect(str(desc)) == 'en':
            print(f"{countfile}. Text:", desc)
            response = comprehend.detect_entities(
                Text=desc,
                LanguageCode='en'
            )

            print(f"{countfile}. Result:", response)
            json.dump(response, open(f'response_aws/{i}_{desc[:10].replace(" ","_")}.json','w'))
            countfile = len(os.listdir('response_aws/'))
            print()

def tocsv():
    text, entities = [], []
    descriptions = json.load(open('descriptions.json'))
    for i, desc in enumerate(descriptions):
        if i == 320:
            continue
        if i > 1756:
            break
        if len(desc) > 20 and detect(str(desc)) == 'en':
            response = json.load(open(f'response_aws/{i+1}_{desc[:10].replace(" ","_")}.json'))
            entities.append([(e['Text'], e['Type']) for e in response['Entities']])
            text.append(desc)
    dfout = pd.DataFrame({'Text': text, 'Entities': entities})
    dfout.to_csv('sample_ner_aws.csv', index=False)

if __name__ == "__main__":
    tocsv()
