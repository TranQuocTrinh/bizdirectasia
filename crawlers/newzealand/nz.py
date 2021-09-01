import selenium
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import json
import requests



def get_detail(soup):
    name = soup.find('h1', class_='title-color')
    general_information = soup.find('div', class_='panel-body')
    dct = {}
    dct['company_name'] = general_information.find('h1', class_='title-color').getText()
    dct['type'] = general_information.find('h1', class_='title-color').parent.getText().split('Type:')[-1].strip('\n')
    #dct['new_zealand_business_number'] =   
    rows = general_information.findAll('div', class_='row')
    data_value = [x.getText() for row in rows for x in row.findAll('div', class_='data-value')]
    data_desc = [x.getText() for row in rows for x in row.findAll('div', class_='data-desc')]
    for x,y in zip(data_desc, data_value):
        print(x, y)

    return dct


def main():
    soup = BeautifulSoup(requests.get('https://www.businesscheck.co.nz/ltd/9429038809910/').text, 'lxml')

    print(get_detail(soup))

if __name__ == '__main__':
    main()