import spacy
import joblib
import numpy as np
from numpy import dot
from numpy.linalg import norm

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from fastapi.responses import JSONResponse

app = FastAPI()


def cos_sim(a, b):
    return dot(a, b)/(norm(a)*norm(b))


class Feature(BaseModel):
    lst_keyword: list


@app.get("/")
async def home():
    return "This is home page!"


@app.post("/keyword_classification_into_naics")
async def keyword_classification_into_naics(item: Feature):
    result = {"lst_naics_code": []}
    vec_keywords = np.zeros((len(item.lst_keyword), 300))
    for i, keyword in enumerate(item.lst_keyword):
        keyword = str(keyword).lower().strip()
        vec_keywords[i] = nlp(keyword).vector

    indexs = cos_sim(vec_keywords, naics_name_vec.T).argmax(axis=1)
    codes = naics_code_vec[indexs]
    rep_codes = [str(c) for c in codes]
    result["lst_naics_code"] = rep_codes

    return JSONResponse(result)


if __name__ == "__main__":
    print("Loading spacy...")
    nlp = spacy.load("en_core_web_lg")

    naics_name_vec = np.load("vec_naics_name.npy")
    naics_code_vec = np.load("word_naics_code.npy")

    uvicorn.run(app, host="0.0.0.0", port=3596)
