'''
import pandas as pd
import os
import json
import joblib
import time
import imp
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from nltk import ngrams
import nltk
import re
import string
from tqdm import tqdm
from fuzzywuzzy import fuzz


def clean_text(text):
    text = text.lower()
    text = re.sub('\[.*?\]', '', text)
    text = re.sub('https?://\S+|www\.\S+', '', text)
    text = re.sub('<.*?>+', '', text)
    text = re.sub('-', ' ', text)
    text = re.sub('\n', ' ', text)
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\w*\d\w*', '', text)
    return text


def text_preprocessing(text):
    tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')
    nopunc = clean_text(text)
    tokenized_text = tokenizer.tokenize(nopunc)
    #remove_stopwords = [w for w in tokenized_text if w not in stopwords.words('english')]
    combined_text = ' '.join(tokenized_text)
    return combined_text



import spacy
# nlp = spacy.load("en_core_web_sm")
dfsearchterms = pd.read_csv('enrich_newzealand.csv')
dfsearchterms = dfsearchterms[dfsearchterms["company_name"].isnull()==False].reset_index(drop=True)
dfsearchterms["company_name"] = dfsearchterms["company_name"].str.lower()#.apply(preprocess_cname)



def getNearestN(query, nbrs, vectorizer):
    queryTFIDF_ = vectorizer.transform(query)
    distances, indices = nbrs.kneighbors(queryTFIDF_)
    return distances, indices


vectorizer = TfidfVectorizer(min_df=0, analyzer='char_wb', max_features=1000)
tf_idf_matrix = vectorizer.fit_transform(list(dfsearchterms['company_name']))
print(tf_idf_matrix.shape)
nbrs = NearestNeighbors(n_neighbors=1, n_jobs=-1).fit(tf_idf_matrix)

def website_matches_fuzzy(text, df, vectorizer, nbrs, threshold=0.8):
    # doc = nlp(text)
    # text = ' '.join([token.text for token in doc if token.pos_ in {'PROPN', 'NOUN'}])
    # query = [' '.join(list(x)) for x in ngrams(text.split(), 3)]
    query = [text]
    distances, indices = getNearestN(query, nbrs, vectorizer)
    matches = []
    for i,j in enumerate(indices):
        score = [round(s,2) for s in distances[i] if s <= (1-threshold)]
        match_sub = [dfsearchterms['company_name'][j[i]] for i,_ in enumerate(score)]
        match_sub_name = list(dfsearchterms[(dfsearchterms.company_name.isin(match_sub))].website.values)
        # temp = [score, query[i], match_sub, match_sub_name]
        for s,m,mn in zip(score, match_sub, match_sub_name):
            temp = {'company_name': query[i], 'company_name_match': m, 'website': mn, 'score':1-s}
            # if 1-s == 1 and query[i] != m:
            #     pass
            # else:
            matches.append(temp)
    return matches



from flashtext import KeywordProcessor
processor = KeywordProcessor(case_sensitive=False)
processor.add_keywords_from_list(list(dfsearchterms['company_name']))

def website_matches_flashtext(text, dfsearchterms, processor):
    lookup_matches = list({n for n in processor.extract_keywords(text, span_info=False)})
    subcategories = list(dfsearchterms[(dfsearchterms.company_name.isin(lookup_matches))].website.values)
    matches = []
    for key, sub in zip(lookup_matches, subcategories):
        temp = {
            'company_name_match': key,
            'website': sub
        }
        matches.append(temp)
    return matches

def way1():
    df = pd.read_csv("biz_newzealand.csv")
    df = df[df["website"].isnull()]
    for i,r in tqdm(df.iterrows(), total=df.shape[0]):
        text = preprocess_cname(r["company_name"].lower())
        # text = r["company_name"].lower()
        # st_time = time.time()
        # matches = website_matches_flashtext(text, dfsearchterms, processor)
        # end_time = time.time()
        # if len(matches) > 0:
        #     print("Text:", text)
        #     print("Exact match:", matches)
        #     print("Time exact match: ", end_time-st_time)
        
        
        st_time = time.time()
        matches = website_matches_fuzzy(text, dfsearchterms, vectorizer, nbrs)
        end_time = time.time()
        if len(matches) > 0:
            print("Text:", r["company_name"])
            print("Fuzzy match:", matches)
            print("Time fuzzy find: ", end_time-st_time)

# =====================================================================================================================================================================================================================
# =====================================================================================================================================================================================================================
# =====================================================================================================================================================================================================================
# =====================================================================================================================================================================================================================
# =====================================================================================================================================================================================================================
# =====================================================================================================================================================================================================================
# =====================================================================================================================================================================================================================
# =====================================================================================================================================================================================================================

def way2():
    import ray
    ray.shutdown()
    ray.init(num_cpus=8)

    df = pd.read_csv("biz_newzealand.csv")
    df = df[df["company_name"].isnull()==False].reset_index(drop=True)
    @ray.remote
    def find_best_match(text):
        scores = [fuzz.token_sort_ratio(text, r["company_name"]) for i,r in tqdm(df.iterrows(), total=len(df))]
        max_score = max(scores)
        idx = [i for i, sc in enumerate(scores) if sc == max_score]
        return [dict(r) for i,r in df.loc[idx, ].iterrows()]
    
    dfenrich = pd.read_csv("enrich_newzealand.csv")
    result_ids = []
    for i,r in dfenrich.iterrows():
        company_name_extract = r["company_name"]
        result_ids.append(find_best_match.remote(company_name_extract))
        if len(result_ids) == 64:
            break
    
    results = ray.get(result_ids)
    import ipdb; ipdb.set_trace()

# =====================================================================================================================================================================================================================
# =====================================================================================================================================================================================================================
# =====================================================================================================================================================================================================================
# =====================================================================================================================================================================================================================
# =====================================================================================================================================================================================================================
# =====================================================================================================================================================================================================================
# =====================================================================================================================================================================================================================
# =====================================================================================================================================================================================================================
'''

# Load libraries
import re
import time
import operator
import datetime
import numpy as np
from sys import getsizeof
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from scipy.sparse import csr_matrix
import pandas as pd
from tqdm import tqdm
import os
import string
import sparse_dot_topn.sparse_dot_topn as ct


def preprocess_cname(company_name, country):
    company_name = str(company_name).lower()
    company_name = re.sub(r'[^\w\s]', '', company_name)
    # common = {'limited', 'ltd', '&', 'snd', 'bhd', 'holdings', 'investments', 'trustee', 'services', 'trustees', 'nz', 'company', 'properties', 'group', 'property', 'zealand', '(nz)'}
    dct_common = {
        'Cambodia': {'ltd.', 'kh', 'construction', 'trading', 'ltd', 'co.,', 'export', 'development', 'investment', 'international', 'import'}, 
        'Laos': {'construction', 'ltd', 'individual', 'sole', 'co.,', 'la', 'lao', 'trading', 'and', 'co.,ltd', 'import-export'}, 
        'Thailand': {'ltd.', 'service', 'co.,', 'co.,ltd.', 'and', 'th', 'partnership', '(thailand)', 'company', 'limited', 'จำกัด'}, 
        'Hong Kong': {'trading', 'group', 'co.,', 'development', 'investment', '(hk)', 'hong', 'international', 'company', 'hk', 'limited'}, 
        'Philippines': {'inc.', 'store', 'trading', 'inc', 'corporation', 'ph', 'shop', 'corp.', 'enterprises', 'services', 'and'}, 
        'Singapore': {'ltd.', 'llp', 'pte', 'trading', 'ltd', 'pte.', 'international', 'services', 'limited', 'engineering', 'sg'}, 
        'Malaysia': {'bhd.', 'my', 'development', 'holdings', 'bhd', 'services', '(m)', 'trading', 'resources', 'sdn.', 'engineering'}, 
        'Taiwan': {'store', 'ltd.', 'tw', 'line', 'co.,', 'enterprise', 'shop', 'engineering', 'international', 'technology', 'industrial'}, 
        'Indonesia': {'abadi', 'perkasa', 'indonesia', 'jaya', 'id', 'prima', 'sejahtera', 'utama', 'karya', 'mandiri', 'mitra'}, 
        'Vietnam': {'thuong', 'tnhh', 'mai', 'ty', 'vn', 'cong', 'stock', 'trading', 'company', 'limited', 'thanh'}, 
        'Korea': {'ltd.', 'farming', 'construction', 'tech', 'association', 'kr', 'co.,', 'co.,ltd.', 'industry', 'korea', 'co.'}, 
        'Japan': {'inc.', 'ltd.', 'joint', 'construction', 'association', 'jp', 'co.,', 'corporation', 'industry', 'company', 'limited'}, 
        'Australia': {'au', 'ltd', 'the', 'superannuation', 'for', 'family', 'pty', 'trustee', 'trust', 'pty.', 'fund'}
        }
    common = dct_common[country]
    company_name = " ".join([w for w in company_name.split(" ") if w not in common])
    return company_name


class StringMatch():
    
    def __init__(self, source_names, target_names):
        self.source_names = source_names
        self.target_names = target_names
        self.ct_vect      = None
        self.tfidf_vect   = None
        self.vocab        = None
        self.sprse_mtx    = None
        
        
    def tokenize(self, analyzer='char_wb', n=3):
        '''
        Tokenizes the list of strings, based on the selected analyzer

        :param str analyzer: Type of analyzer ('char_wb', 'word'). Default is trigram
        :param str n: If using n-gram analyzer, the gram length
        '''
        # Create initial count vectorizer & fit it on both lists to get vocab
        self.ct_vect = CountVectorizer(analyzer=analyzer, ngram_range=(n, n))
        self.vocab   = self.ct_vect.fit(self.source_names + self.target_names).vocabulary_
        
        # Create tf-idf vectorizer
        self.tfidf_vect  = TfidfVectorizer(vocabulary=self.vocab, analyzer=analyzer, ngram_range=(n, n))
        
        
    def bytesto(bytes, to, bsize=1024): 
        a = {'k' : 1, 'm': 2, 'g' : 3, 't' : 4, 'p' : 5, 'e' : 6 }
        r = float(bytes)
        return bytes / (bsize ** a[to])
        

    def match(self, ntop=1, lower_bound=0.5, output_fmt='df'):
        '''
        Main match function. Default settings return only the top candidate for every source string.
        
        :param int ntop: The number of top-n candidates that should be returned
        :param float lower_bound: The lower-bound threshold for keeping a candidate, between 0-1.
                                   Default set to 0, so consider all canidates
        :param str output_fmt: The output format. Either dataframe ('df') or dict ('dict')
        '''
        self._awesome_cossim_top(ntop, lower_bound)
        
        if output_fmt == 'df':
            match_output = self._make_matchdf()
        elif output_fmt == 'dict':
            match_output = self._make_matchdict()
            
        return match_output
        
        
    def _awesome_cossim_top(self, ntop, lower_bound):
        ''' https://gist.github.com/ymwdalex/5c363ddc1af447a9ff0b58ba14828fd6#file-awesome_sparse_dot_top-py '''
        # To CSR Matrix, if needed
        A = self.tfidf_vect.fit_transform(self.source_names).tocsr()
        B = self.tfidf_vect.fit_transform(self.target_names).transpose().tocsr()
        M, _ = A.shape
        _, N = B.shape

        idx_dtype = np.int32

        nnz_max = M * ntop

        indptr = np.zeros(M+1, dtype=idx_dtype)
        indices = np.zeros(nnz_max, dtype=idx_dtype)
        data = np.zeros(nnz_max, dtype=A.dtype)

        ct.sparse_dot_topn(
            M, N, np.asarray(A.indptr, dtype=idx_dtype),
            np.asarray(A.indices, dtype=idx_dtype),
            A.data,
            np.asarray(B.indptr, dtype=idx_dtype),
            np.asarray(B.indices, dtype=idx_dtype),
            B.data,
            ntop,
            lower_bound,
            indptr, indices, data)

        self.sprse_mtx = csr_matrix((data,indices,indptr), shape=(M,N))
    
    
    def _make_matchdf(self):
        ''' Build dataframe for result return '''
        # CSR matrix -> COO matrix
        cx = self.sprse_mtx.tocoo()

        # COO matrix to list of tuples
        match_list = []
        for row,col,val in zip(cx.row, cx.col, cx.data):
            match_list.append((row, self.source_names[row], col, self.target_names[col], val))

        # List of tuples to dataframe
        colnames = ['source_idx', 'company_name', 'target_idx', 'candidate_company_name', 'score']
        match_df = pd.DataFrame(match_list, columns=colnames)

        return match_df

    
    def _make_matchdict(self):
        ''' Build dictionary for result return '''
        # CSR matrix -> COO matrix
        cx = self.sprse_mtx.tocoo()

        # dict value should be tuple of values
        match_dict = {}
        for row,col,val in zip(cx.row, cx.col, cx.data):
            if match_dict.get(row):
                match_dict[row].append((col,val))
            else:
                match_dict[row] = [(col, val)]

        return match_dict



def get_data_es(country, size, from_id=0):
    import requests
    import json

    url = "http://esbk.bizdirectasia.com/companies/_search"

    payload = json.dumps({
    "query": {
        "bool": {
        "must": [
            {
            "range": {
                "id": {
                "gt": from_id
                }
            }
            },
            # {
            # "exists": {
            #     "field": "website"
            # }
            # },
            # {
            # "exists": {
            #     "field": "founded_address"
            # }
            # },
            {
            "exists": {
                "field": "company_name"
            }
            },
            {
            "match": {
                "country_name": country
            }
            }
        ]
        }
    },
    "_source": [
        "id",
        "website",
        "company_name",
        "current_address",
        "founded_address",
        "country_name"
    ],
    "sort": [
        {
        "id": "asc"
        }
    ],
    "size": size
    })
    headers = {
    'Authorization': 'Basic YWJyYWhhbTpwQGliVmVIJSVUQlkwdHA3V3NCcGJ6eWE2',
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    response = json.loads(response.text)["hits"]["hits"]
    rep = [response[i]["_source"] for i in range(len(response))]
    return rep
    # df = pd.DataFrame([response[i]["_source"] for i in range(len(response))])
    # return df


def get_data_country(country):
    print("GET data Bizdirect from Elasticsearch...")
    from_id = 0
    all_company = []
    while True:
        os.system("clear")
        print("Length df_enrich:", len(all_company))
        size = 10000
        temp = get_data_es(country, size, from_id)
        if len(temp) > 0:
            all_company.extend(temp)
            from_id = temp[-1]["id"]
        else:
            break
    return pd.DataFrame(all_company)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv_biz_path", default="", type=str,required=False, help="Path of bizdirect data",)
    parser.add_argument("--csv_enrich_path", default="enrich_newzealand.csv", type=str,required=False, help="Path of enrich data",)
    parser.add_argument("--country", default="New Zealand", type=str,required=False, help="Country runing",)
    parser.add_argument("--output_final_csv_path", default="result_matching.csv", type=str,required=False, help="Country runing",)
    parser.add_argument("--threshold", default=0.8, type=float,required=False, help="Threshold",)
    args = parser.parse_args()

    if args.csv_biz_path == "":
        dfenr = get_data_country(args.country)
        args.csv_biz_path = f"biz_{args.country.lower().replace(' ','_')}.csv"
        dfenr.to_csv(args.csv_biz_path, index=False)
        
    class biz_info:
        path = args.csv_biz_path
        company_name = "company_name"
    
    class enrich_info:
        path = args.csv_enrich_path
        company_name = "company_name_extract"
        website = "website"
    

    dfbiz = pd.read_csv(biz_info.path)
    dfbiz = dfbiz[dfbiz[biz_info.company_name].isnull()==False].reset_index(drop=True)
    source_name = dfbiz[biz_info.company_name].tolist()

    dfenrich = pd.read_csv(enrich_info.path)#.sample(n=18763, random_state=42)
    dfenrich = dfenrich[dfenrich[enrich_info.company_name].isnull()==False].reset_index(drop=True)
    target_name = dfenrich[enrich_info.company_name].tolist()


    cname_match = StringMatch(source_name, target_name)
    t0 = datetime.datetime.now()
    cname_match.tokenize()
    print("Matching...")
    match_df = cname_match.match()
    t1 = datetime.datetime.now()

    full_time_tfidf = int((t1-t0).total_seconds())
    full_time_tfidf = str(datetime.timedelta(seconds=full_time_tfidf))
    print(f"Total time: {full_time_tfidf}")

    # match_df = match_df[match_df["score"] > args.threshold]
    def update_score(match_df):
        new_scores = []
        dif, le = [], []
        for i,r in match_df.iterrows():
            src_process = preprocess_cname(r["company_name"], args.country)
            tar_process = preprocess_cname(r["candidate_company_name"], args.country)
            src = len(src_process)
            tar = len(tar_process)
            if src_process == tar_process:
                if len(tar_process.split(" ")) > 1:
                    difference_score, length_score, s = 0, 1, 1
                else:
                    difference_score, length_score, s = 0, 1, 0.5
            else:
                difference_score = abs(src - tar)/max(src, tar) if max(src, tar) != 0 else 0
                tar = len(r["candidate_company_name"])
                length_score = tar/20 if tar < 20 else 1.
                s = length_score*0.2 + r["score"]*0.8 - difference_score*0.5
            
            new_scores.append(s)
            dif.append(difference_score)
            le.append(length_score)
        
        match_df["final_score"] = new_scores
        match_df["difference_score"] = dif
        match_df["length_score"] = le
        return match_df

    match_df = update_score(match_df)
    # match_df = match_df[match_df["final_score"] > args.threshold]

    results = []
    for i,r in tqdm(match_df.iterrows(), total=len(match_df)):
        res = dict(dfbiz.iloc[r["source_idx"]])
        res["website_matching"] = dfenrich.iloc[r["target_idx"]][enrich_info.website]
        res["company_name_extract"] = dfenrich.iloc[r["target_idx"]][enrich_info.company_name]
        res["final_score"] = r["final_score"]
        res["score"] = r["score"]
        res["difference_score"] = r["difference_score"]
        res["length_score"] = r["length_score"]
        results.append(res)

    dfout = pd.DataFrame(results)
    dfout = dfout[dfout["final_score"]>=args.threshold]
    dfout = dfout[['id', 'country_name', 'website', 'company_name', 'company_name_extract', 'website_matching', 'final_score']]
    dfout.to_csv(args.output_final_csv_path, index=False)
    print(f"Result save at path: {args.output_final_csv_path}")
    print()
    print(f"Extract contact and Matching website - {args.country}")
    print(f"Total domains {dfenrich.shape[0]} extracted company_name")
    print(f"Total company of bizdirect {dfbiz.shape[0]}")
    print(f"Total number of matching websites {dfout.shape[0]} (with threshold={args.threshold}), of which {dfout[dfout['website'].isnull()==False].shape[0]} already have websites, in the end there are {dfout[dfout['website'].isnull()].shape[0]} matched websites.")
    

def get_word_common(df, code):
    from collections import Counter
    tmp = []
    for cname in df.company_name:
        tmp.extend(str(cname).lower().split(" "))
    count = dict(Counter(tmp))
    sor = sorted([(k,v) for k,v in count.items()], key=lambda x: x[1], reverse=True)
    sor = [x for x in sor if len(x[0]) > 1]
    common = set([x[0] for x in sor[:10]])
    common.add(code)
    return common


if __name__ == '__main__':
    main()


