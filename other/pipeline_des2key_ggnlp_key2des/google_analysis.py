# Imports the Google Cloud client library
from google.cloud import language_v1 as gnl
from google.oauth2 import service_account as svc
from ratelimit import limits, sleep_and_retry

import json
import logging
import pandas as pd

logging.basicConfig(level = logging.INFO)

class GoogleNL:
    # RATE_LIMIT_MIN = 600   
    def __init__(self, credential_path: str):
        self.credentials = svc.Credentials.from_service_account_file(credential_path)
        
    # @sleep_and_retry
    # @limits(calls = RATE_LIMIT_MIN, period = 60)
    # def check_limit(self):
    #     return

    def full_analyze_text(self, text: str) -> dict:
        # self.check_limit()
        doc = gnl.Document(content = text, type_ = gnl.Document.Type.PLAIN_TEXT)
        client = gnl.LanguageServiceClient(credentials = self.credentials)
        
        features = {
                        'extract_document_sentiment': True,
                        'extract_syntax':True,
                        'extract_entities': True,
                        'extract_entity_sentiment':True,
                   }
        feature_classify = {
            'classify_text': True
        }

        try:
            request = gnl.AnnotateTextRequest(document = doc, features = features)
            response = client.annotate_text(request = request)
            result_json = response.__class__.to_json(response)
            result_dict = json.loads(result_json)
        except:
            return {}
        
        try:
            request_classify = gnl.AnnotateTextRequest(document = doc, features = feature_classify)
            response_classify = client.annotate_text(request = request_classify)
        except:
            response_classify = None
        result_dict["categories"] = self.parser_response_classify(response_classify)
        result_dict = {k:json.dumps(v) for k,v in result_dict.items()}
        return result_dict
    
    def parser_response_classify(self, response):
        if response is None:
            return "Error"
        else:
            result_json = response.__class__.to_json(response)
            result_dict = json.loads(result_json)
        
            return json.dumps(result_dict["categories"])
    

CREDENTIAL_PATH = "/home/pvduy/web-architecture-migration-quoc-trinh.json"

df = pd.read_csv("10k_example_data.csv")

from tqdm import tqdm

#Google built models internally (neural nets) and exposing them via the API
client = GoogleNL(CREDENTIAL_PATH)
count_request = 0
new_df = []
bar = tqdm(df.iterrows(), total=df.shape[0])
for i, row in bar:
    text = row["desc"]
    ta = client.full_analyze_text(text=text)
    json.dump(ta, open(f"cache/{row['id']}.json", "w"))
    new_df.append(dict(row, **ta))
    count_request = count_request +1

    bar.set_postfix({"request": count_request})

new_df = pd.DataFrame(new_df)
print(new_df.head())
new_df.to_csv("10k_example_data_with_ggnlp.csv", index=False)

# language_v1.Entity.Type(2).name