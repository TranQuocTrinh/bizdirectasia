# Define of the problem
How to summarize content of a website, input is a website url, output is a description of the website.

Example:
```
Input: https://bizdirectasia.com/
Output: BizDirect Asia is Asia's largest B2B contacts and companies data portal emcompassed more than 18+ millions companies and 90 millions contacts across 1,000+ industries in 16 countries in Asia. Updated in real-time by our proprietary AI-powered system.
```

# Collect data

Path: data_collect/crawl_cbinsights.com.py

For collecting data, use the following command:

```bash
cd data_collect && python crawl_cbinsights.com.py
```

The data will be saved in the data_collect/data_cbinsights.csv file.
Some rows in the data_cbinsights.csv file shown below:

```
In [22]: df = pd.read_csv("data_cbinsights.csv")

In [23]: df
Out[23]: 
                      company_name                                                url  ...                                        description          source
0       Center Point Manufacturing  https://www.cbinsights.com/company/center-poin...  ...  Center Point Manufacturing is a provider of Ho...  cbinsights.com
1                          Navizon         https://www.cbinsights.com/company/navizon  ...  Navizon is a software provider for mobile devi...  cbinsights.com
2                          Artspan         https://www.cbinsights.com/company/artspan  ...  Artspan is an online gallery of original artwo...  cbinsights.com
3                            Ideel          https://www.cbinsights.com/company/ideeli  ...  Ideel is a members-only real-time shopping com...  cbinsights.com
4               Brightside Academy  https://www.cbinsights.com/company/brightside-...  ...  Brightside Academy, Inc. is a chain of child c...  cbinsights.com
...                            ...                                                ...  ...                                                ...             ...
629202              PDT Solicitors  https://www.cbinsights.com/company/pdt-solicitors  ...  PDT Solicitors is a commercial law practice sp...  cbinsights.com
629203               Fintech Scion   https://www.cbinsights.com/company/fintech-scion  ...  Fintech Scion offers a platform as a service (...  cbinsights.com
629204  TIEFENBACH Control Systems  https://www.cbinsights.com/company/tiefenbach-...  ...  TIEFENBACH Control Systems manufactures a vari...  cbinsights.com
629205                Pearl Global    https://www.cbinsights.com/company/pearl-global  ...  Pearl Global (NSE: PGIL) designs and manufactu...  cbinsights.com
629206              Alpha Clothing  https://www.cbinsights.com/company/alpha-clothing  ...  Alpha Clothing offers apparel manufacturing se...  cbinsights.com

[629207 rows x 5 columns]
```

