import psycopg2
import pandas as pd
from tqdm import tqdm
import os
import time


connection = psycopg2.connect(
    user="bda",
    password="123456@qwer",
    host="52.221.188.178",
    port="5432",
    database="etl_bizdirect_app"
    )

def query_keyword(offset=0, limit=1000):
    cursor = connection.cursor()
    if limit == 0:
        query = "select c.company_id, c.company_key, c.company_name, string_agg(k.keyword, ',') as keywords \
                from company_keyword_mapping_v2 k inner join es_comp_v2 c on c.company_id = k.company_id \
                group by c.company_id, c.company_key, c.company_name order by company_id"# limit {} offset {}".format(limit, offset)
    else:
        query = "select c.company_id, c.company_key, c.company_name, string_agg(k.keyword, ',') as keywords \
                from company_keyword_mapping_v2 k inner join es_comp_v2 c on c.company_id = k.company_id \
                group by c.company_id, c.company_key, c.company_name order by company_id limit {} offset {}".format(limit, offset)

    cursor.execute(query)
    print('Query Done!')
    df = {
        'company_id': [],
        'company_key': [],
        'company_name': [],
        'keyword': [],
    }
    for row in tqdm(cursor.fetchall()):
        df['company_id'].append(row[0])
        df['company_key'].append(row[1])
        df['company_name'].append(row[2])
        df['keyword'].append(row[3])

    cursor.close()
    return pd.DataFrame(df)

def main():
    offset, limit = 0, 0
    st_time = time.time()
    df = query_keyword(offset, limit) # limit=0 is call all data
    fname = os.path.join(str(offset)+'_'+str(offset+limit)+'.csv')
    df.to_csv(fname, index=False)
    print('File name: {}, Time: {}'.format(fname, time.time()-st_time))

if __name__ == '__main__':
    main()