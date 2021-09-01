import time
import selenium
from selenium import webdriver
from bs4 import BeautifulSoup
import json
import pandas as pd
import csv


def create_driver():
    address = '68.183.179.248:3128'
    options = webdriver.ChromeOptions()
    options.add_argument('--proxy-server=%s' % address)
    driver = webdriver.Chrome()#options=options, chrome_options=chrome_options)
    driver.get('https://sgpgrid.com/search-results')
    time.sleep(20)
    return driver

# driver = webdriver.Chrome()
# driver.get('https://sgpgrid.com/search-results')
# time.sleep(20)

driver = create_driver()

RESULT = ['company_name', 'business_description', 'contact_no', 'email', 'url', 'address', 'industry_type', 
            'registration_number', 'incorporation_date', 'company_type']
with open('output.csv','a') as result_file:
    wr = csv.writer(result_file, dialect='excel')
    wr.writerow(RESULT)

count = 0
while True:
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    rows = soup.findAll('div', class_='rt-tr -odd')
    for row in rows:
        ROW = [x.getText() for x in row.findAll('div')]
        with open('output.csv','a') as result_file:
            wr = csv.writer(result_file, dialect='excel')
            wr.writerow(ROW)
            count += 1

    print(count)
    driver.find_element_by_css_selector('#__next > div.content > section > div > div > div.col-xl-12.col-lg-12 > div > div > div.company-table-footer-button-block > div.company-table-footer-navigation > button:nth-child(2)').click()
    time.sleep(2)
