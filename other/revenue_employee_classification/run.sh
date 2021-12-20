#!/bin/bash

sudo apt-get install python3-pip
sudo pip3 install virtualenv
virtualenv vlen3
source vlen3/bin/activate

pip install -U pip
pip install torch numpy flask requests
