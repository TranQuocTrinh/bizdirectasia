# coding: utf-8
# from p_tqdm import p_map
# import pandas as pd
import pickle
from flask import Flask, Response, jsonify, request
from flask import Request
import os
import json
import requests
app = Flask(__name__)

from func_timeout import func_timeout, FunctionTimedOut, func_set_timeout

@func_set_timeout(60.0)
def getevent():
    em = json.load(open("./data_trade/alldata.json"))
    try:
        return em
    except:
        return []

@app.route("/asiaevents", methods=['GET', 'POST'])
def asiaevents():
    try:
        res = getevent()
        # print(res)
        return jsonify({'event': res})
    except:
        return jsonify({'event': []})


if __name__ == "__main__":
    app.run("0.0.0.0", port=2334, debug=True)
