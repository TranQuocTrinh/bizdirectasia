#!/bin/bash

sudo apt-get install python3-pip
sudo pip3 install virtualenv
virtualenv vlen3
source vlen3/bin/activate

pip3 install -U pip
pip3 install flask joblib tqdm torch transformers pandas numpy scikit-learn fastapi uvicorn pydantic