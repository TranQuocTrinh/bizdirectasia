import selenium
from selenium import webdriver
import time
from bs4 import BeautifulSoup
import json
from tqdm import tqdm


def search(search):
    driver = webdriver.PhantomJS()
    driver.get('https://www.mysbusiness.com/search')
    driver.find_element_by_css_selector('#search_val').send_keys(search+'\n')
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, 'lxml')
    lst_href = soup.find('div', class_='list-group').find_all('a')

    company_name = [x.find('h4').getText() for x in lst_href]

    registration_no = [x.find('p').getText() for x in lst_href]
    driver.close()

    return [{'company_name':k, 'registration_no':v} for k,v in zip(company_name, registration_no)]

import sys
import tqdm
# len_string = int(sys.argv[1])

chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
chars = [x for x in chars]

for x in chars:
    for y in chars:
        for z in chars:
            s = x+y+z
            try:
                data = search(s)
            except:
                data = []

            print(data)
            print(len(data))
            print(s)
            if len(data) != 0:
                json.dump(data,open('data_mys/'+ s +'.json','w'))

