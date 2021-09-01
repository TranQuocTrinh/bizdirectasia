import numpy as np
from tqdm import tqdm
from flask import Flask, Response, jsonify, request
from flask import Request
import os
import json
import requests
import joblib
import spacy
import string

app = Flask(__name__)


def preprocessing(s):
    s = str(s).strip().lower()
    s = ' '.join(s.split())
    s = s.translate(str.maketrans('', '', string.punctuation))
    return s

def classify(centroid_matrix, model, lst_sub_category_code, keyword):
    word_embed_vector = model(preprocessing(keyword)).vector
    dist = (centroid_matrix - word_embed_vector)**2
    dist = np.sum(dist, axis=1)
    dist = np.sqrt(dist)
    index = dist.argmin()
    return lst_sub_category_code[index]


@app.route('/keyword_category', methods=['POST'])
def keyword_category():
    # try:
        keyword = request.form['keyword']
        subcode = classify(centroid_matrix, nlp, list(dct_code_info.keys()), keyword)
        sub_category_name = dct_code_info[subcode]['sub_category_name']
        category_code = dct_code_info[subcode]['category_code']
        category_name = dct_code_info[subcode]['category_name']

        return jsonify({
            'category_code': category_code,
            'category_name': category_name,
            'sub_category_code': subcode,
            'sub_category_name': sub_category_name,
        })

if __name__ == "__main__":
    nlp = spacy.load('en_core_web_lg')
    all_keywords_label = joblib.load('library/all_keywords_label.joblib')
    dct_code_info = joblib.load('library/dct_code_info.joblib')
    all_keywords_need_classify = joblib.load('library/all_keywords_need_classify.joblib')
    centroid_matrix = np.load('library/centroid_matrix.npy')

    app.run("0.0.0.0", port=2201, debug=True)