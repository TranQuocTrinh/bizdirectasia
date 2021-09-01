import pandas as pd
from tqdm import tqdm

dct = {
    'sg': 'singapore',
    'ph': 'philippines',
    'kr': 'south_korea',
    'tw': 'taiwan',
    'my': 'malaysia',
    'jp': 'japan',
    'vn': 'vietnam',
    'id': 'indonesia',
    'nz': 'new_zealand',
    'hk': 'hongkong',
    'kh': 'cambodia',
    'la': 'laos',
    'mm': 'myanmar',
    'th': 'thailand',
    'au': 'australia',
    'bn': 'brunei'
}

def main():
    # read_csv
    print("Read csv ....")
    df = pd.read_csv('host10m.csv')

    results = {x:[] for x in list(dct.values())}

    if 0:
        until = 100
    else:
        until = len(df)

    dot = set(dct.keys())
    for i in tqdm(range(until)):
        url = df.iloc[i]["google.com"]
        aftdot = url.split('.')[-1]
        if aftdot in dot:
            results[dct[aftdot]].append(url)

    for key in results:
        if len(results[key]) != 0:
            df = pd.DataFrame({key:results[key]})
            df.to_csv('split/'+key+'.csv', index=False)

if __name__=="__main__":
    main()