import pandas as pd
import json
import os
from tqdm import tqdm
from langdetect import detect
from transformers import AutoTokenizer
from sklearn.model_selection import train_test_split

df = pd.read_csv("/home/pvduy/tqtrinh/bizdirectasia/website2description/data_collect/data_cbinsights.csv")
print(df)
def main():
    # Load data
    cache_dir = "/home/pvduy/tqtrinh/bizdirectasia/website2description/data_collect/cache_cbinsights_content"
    files = os.listdir(cache_dir)
    bar = tqdm(files, total=len(files), desc="Loading data")
    data = []
    for file in bar:
        cache = json.load(open(os.path.join(cache_dir, file)))
        if cache["content"] is not None and cache["content"] != "":
            data.append(cache)
        
        bar.set_postfix({"len data": len(data)})
    
    data = pd.DataFrame(data)
    bar = tqdm(data.iterrows(), total=len(data), desc="Detect language")
    for i, row in bar:
        try:
            lang = detect(row["content"])
        except:
            lang = "unknow"
        data.loc[i, "language"] = lang
    data = data[data["language"]=="en"].reset_index(drop=True)

    # Join with df by website
    data = pd.merge(df, data, how='inner', on = 'website')
    
    # len(tokens)
    tokenizer = AutoTokenizer.from_pretrained("allenai/led-base-16384")
    data["len_content"] = data["content"].apply(lambda x: len(tokenizer.tokenize(x)))
    data = data[data["len_content"] >= 300]
    data = data[data["len_content"] <= 2048]

    # Plot len_content
    import matplotlib.pyplot as plt
    plt.figure()
    plt.hist(data["len_content"], bins=100)
    # save figure
    plt.savefig("len_content.png")

    # Sort columns
    data = data[['company_name', 'website', 'description', 'content', 'about_us_url', 'about_us_content', 'url', 'source', 'language']]

    # Split train, val, test
    test = data.sample(n=5000, random_state=42)
    train = data.drop(test.index)
    train, val = train_test_split(train, test_size=0.1, random_state=42)
    train, val, test = train.reset_index(drop=True), val.reset_index(drop=True), test.reset_index(drop=True)
    if not os.path.exists("../src/data"):
        os.mkdir("../src/data")
    train.to_csv("../src/data/train.csv", index=False)
    val.to_csv("../src/data/val.csv", index=False)
    test.to_csv("../src/data/test.csv", index=False)

    print("Train:", len(train), "save to ../src/data/train.csv")
    print("Val:", len(val), "save to ../src/data/val.csv")
    print("Test:", len(test), "save to ../src/data/test.csv")
    import ipdb; ipdb.set_trace()
    return data


if __name__ == "__main__":
    main()