from numpy.core.defchararray import index, lower
import ipdb
import spacy
import joblib
import numpy as np
from tqdm import tqdm
from sklearn.cluster import KMeans
import pandas as pd
import ast
from numpy import dot
from numpy.linalg import norm


def cos_sim(a, b):
    return dot(a, b)/(norm(a)*norm(b))


def clustering():
    nlp = spacy.load("en_core_web_lg")

    all_keywords_path = "/home/ubuntu/tqtrinh/description2keywords/data/japan/all_keywords.joblib"
    all_keywords = joblib.load(all_keywords_path)
    all_keywords = [keyword.lower().strip()
                    for keyword in all_keywords.values()]

    bar = tqdm(enumerate(all_keywords), total=len(
        all_keywords), desc="Word Embedding...")
    X = np.zeros((len(all_keywords), 300))
    for i, keyword in bar:
        doc = nlp(keyword)
        X[i] = doc.vector
    all_keywords = np.array(all_keywords)

    np.save("vec_all_keywords.npy", X)
    np.save("word_all_keywords.npy", all_keywords)

    df_naics = pd.read_csv("ISIC_NAICS_keywords_mapping_final.csv")
    n_clusters = len(set(df_naics["NAICS Code"].values))
    print(f"Clustering keyword data into {n_clusters} clusters...")
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, verbose=1).fit(X)
    joblib.dump(kmeans, "kmean_cluster.joblib")

    pred_classes = kmeans.predict(X)
    df_clus = []
    for cluster in range(n_clusters):
        temp = dict(
            trinh_cluster_code=cluster,
            baseconnect_keywords=list(
                all_keywords[np.where(pred_classes == cluster)])
        )
        df_clus.append(temp)
    df_clus = pd.DataFrame(df_clus)
    df_clus.to_csv("clustering_baseconnect_keywords.csv", index=False)

    # matching
    dct_naics = {r["NAICS Code"]: dict(r) for i, r in df_naics.iterrows()}
    naics_code_vec = np.array(list(dct_naics.keys()))
    naics_name_vec = np.zeros((len(naics_code_vec), 300))
    for i, code in tqdm(enumerate(naics_code_vec), total=len(naics_code_vec)):
        naics_name_vec[i] = nlp(dct_naics[code]["NAICS Name"].lower()).vector
    np.save("word_naics_code.npy", naics_code_vec)
    np.save("vec_naics_name.npy", naics_name_vec)


# matching


def index_similarity_keywords_naics_name(vec_keywords, vec_naics_name):
    score = cos_sim(vec_keywords, vec_naics_name.T).mean(axis=0)
    return score.argmax()


def matching():
    X = np.load("vec_all_keywords.npy")
    all_keywords = np.load("word_all_keywords.npy")

    naics_name_vec = np.load("vec_naics_name.npy")
    naics_code_vec = np.load("word_naics_code.npy")

    df_clus = pd.read_csv("clustering_baseconnect_keywords.csv")
    df_clus["baseconnect_keywords"] = df_clus["baseconnect_keywords"].map(
        lambda lst: ast.literal_eval(lst))

    df_naics = pd.read_csv("ISIC_NAICS_keywords_mapping_final.csv")

    dct_naics = {r["NAICS Code"]: dict(r) for i, r in df_naics.iterrows()}

    kmeans = joblib.load("kmean_cluster.joblib")

    df_out = []
    pred_classes = kmeans.predict(X)
    index_remain = [i for i in range(len(naics_code_vec))]
    bar = tqdm(range(kmeans.n_clusters))
    print(len(set(naics_code_vec)))
    check_naics_code_matching = set()
    for cluster in bar:
        vec_keys = X[np.where(pred_classes == cluster)]
        vec_naics_remain = naics_name_vec[index_remain]
        vec_naics_code_remain = naics_code_vec[index_remain]

        index_matching = index_similarity_keywords_naics_name(
            vec_keys, vec_naics_remain)
        naics_code_matching = vec_naics_code_remain[index_matching]
        old_len = len(check_naics_code_matching)
        check_naics_code_matching.add(naics_code_matching)
        new_len = len(check_naics_code_matching)
        if new_len == old_len:
            import ipdb
            ipdb.set_trace()
        #
        temp = dct_naics[naics_code_matching]
        temp["trinh_cluster_code"] = cluster
        temp["baseconnect_keywords"] = list(
            all_keywords[np.where(pred_classes == cluster)])
        df_out.append(temp)

        # update
        del index_remain[index_matching]

        bar.set_postfix(remain=len(index_remain), cluster=cluster,
                        len_code_match=len(check_naics_code_matching))

    df_out = pd.DataFrame(df_out)
    sorted_cols = ["trinh_cluster_code"] + \
        list(df_naics.columns) + ["baseconnect_keywords"]
    df_out = df_out[sorted_cols]
    print(df_out.head(20))
    df_out.to_csv("NAICS_baseconnect_matching.csv", index=False)


def matching2():
    X = np.load("vec_all_keywords.npy")
    all_keywords = np.load("word_all_keywords.npy")

    naics_name_vec = np.load("vec_naics_name.npy")
    naics_code_vec = np.load("word_naics_code.npy")

    df_clus = pd.read_csv("clustering_baseconnect_keywords.csv")
    df_clus["baseconnect_keywords"] = df_clus["baseconnect_keywords"].map(
        lambda lst: ast.literal_eval(lst))

    df_naics = pd.read_csv("ISIC_NAICS_keywords_mapping_final.csv")

    dct_naics = {r["NAICS Code"]: dict(r) for i, r in df_naics.iterrows()}
    dct_matching = {k: [] for k in dct_naics.keys()}

    indexs = cos_sim(X, naics_name_vec.T).argmax(axis=1)
    codes = naics_code_vec[indexs]

    for key, code in zip(all_keywords, codes):
        dct_matching[code].append(key)

    df_out = []
    for k in dct_naics:
        temp = dct_naics[k]
        temp["baseconnect_keywords"] = dct_matching[k]
        df_out.append(temp)

    df_out = pd.DataFrame(df_out)
    sorted_cols = list(df_naics.columns) + ["baseconnect_keywords"]
    df_out = df_out[sorted_cols]
    print(df_out.head(20))
    df_out.to_csv("NAICS_baseconnect_matching_new_way.csv", index=False)


if __name__ == "__main__":
    matching()
