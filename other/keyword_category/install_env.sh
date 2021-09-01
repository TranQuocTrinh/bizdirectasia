#!/bin/bash

sudo apt-get install python3-pip
sudo pip3 install virtualenv
virtualenv vlen3
source vlen3/bin/activate

pip3 install -U pip
pip3 install spacy flask joblib tqdm
python3 -m spacy download en_core_web_lg