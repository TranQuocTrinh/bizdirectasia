import os
import pandas as pd
from sqlalchemy import create_engine, event
import psycopg2
import psycopg2.extras
import pickle
import pyodbc
import mysql.connector

# Bizdirect PostgresSQL
pgbiz_connd={
    "user": "bizsearch",
    "password": "Bizse@rch",
    "dbname": "bizsearch",
    "host": "54.251.79.117",
    "port": "30543"
    }

pgbiz_engine_url='postgresql://bizsearch:Bizse@rch@54.251.79.117:30543/bizsearch'


def pgbiz_engine():
    return create_engine(pgbiz_engine_url,use_batch_mode=True)

def pgbiz_connect():
    return psycopg2.connect(**pgbiz_connd)

def qry_tpl_pgbiz(sql):
    with pgbiz_connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

def qry_df_pgbiz(sql):
    with pgbiz_connect() as conn:
        return pd.read_sql(sql, conn)

def cmd_pgbiz(sql):
    with pgbiz_connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            try:
                rt=cursor.fetchall() #return value
            except:
                rt=None
            return rt

df = qry_df_pgbiz(
    """
    select tb3.name as country
        , tb1.*
        , tb1.tradestyle as name_call_clearbit
        , tb2.name_result as name_tu_clearbit
        , tb2.domain, tb2.results as result_extract
    from company tb1 inner 
        join result_extract_data tb2 on tb1.id = tb2.company_id 
        join country tb3 on tb1.country_id = tb3.id
    """
)

df.to_csv('data_for_name_matching_sql.csv', index=False)