# Define of the problem
How to summarize content of a website, input is a website url, output is a description of the website.

Example:
```
Input: https://bizdirectasia.com/
Output: BizDirect Asia is Asia's largest B2B contacts and companies data portal emcompassed more than 18+ millions companies and 90 millions contacts across 1,000+ industries in 16 countries in Asia. Updated in real-time by our proprietary AI-powered system.
```

# Directory structure
```
web2description
├── README.md
├── data_collect
│   ├── crawl_cbinsights.com.py
│   ├── create_train_val_test.py
│   ├── get_content.py
│   └── progress_bar.py
└── src
    ├── data
    │   ├── data_analysis.ipynb
    │   ├── test.csv
    │   ├── train.csv
    │   └── val.csv
    ├── data_clean
    ├── inference.py
    ├── train_clm.py
    ├── utils.py
    └── web2des-led
```

# Collect data
## Collect website and description from [cbinsights](https://cbinsights.com/)
Path: data_collect/crawl_cbinsights.com.py

For collecting data, use the following command:

```bash
cd data_collect && python crawl_cbinsights.com.py
```

The data will be saved in the data_collect/data_cbinsights.csv file.
Some rows in the data_cbinsights.csv file shown below:

```
In [1]: df = pd.read_csv("data_cbinsights.csv")

In [2]: df
Out[2]: 
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

## Collect content from websites

**workdir: ./data_collect/**

For collecting data from cbinsights.com, use the following command:

```bash
python crawl_cbinsights.com.py
```

For collecting data, use the following command:
```bash
python get_content.py --get_content
```

For check status of the crawler, use the following command:
```bash
python get_content.py --statis
```

# Model

We use the LED model to summarize the content of the website. Specifically, we use the `allenai/led-base-16384` model.


# Training

**workdir: ./src/**

For training, use the following command:
```bash
python train_clm.py \
    --model_name_or_path allenai/led-base-16384 \
    --do_train --do_eval --do_predict \
    --output_dir web2des-led-filtered \
    --train_file data/train_filtered.csv \
    --validation_file data/val_filtered.csv \
    --test_file data/test_filtered.csv \
    --num_epochs 3 \
    --max_source_length 1024 \
    --max_target_length 256 \
    --logging_steps 100 \
    --eval_steps 3000 \
    --save_steps 3000 \
    --batch_size 6 \
    --batch_size_val 6 \
    --overwrite_output_dir \
    --early_stopping_patience 100 \
    --metric_for_best_model rouge2 
```

For debugging, use the following command:
```bash
python train_clm.py \
    --model_name_or_path allenai/led-base-16384 \
    --do_train --do_eval --do_predict \
    --output_dir web2des-led \
    --train_file data/train.csv \
    --validation_file data/val.csv \
    --test_file data/test.csv \
    --num_epochs 1 \
    --max_source_length 2048 \
    --max_target_length 256 \
    --logging_steps 1 \
    --eval_steps 2 \
    --save_steps 2 \
    --batch_size 4 \
    --batch_size_val 4 \
    --early_stopping_patience 100 \
    --metric_for_best_model rouge2 \
    --max_train_samples 1 \
    --max_eval_samples 1 \
    --max_predict_samples 1
```

# Inference

For inference, use the following command:
```bash
python inference.py \
    --model_path led_web2desc
```
