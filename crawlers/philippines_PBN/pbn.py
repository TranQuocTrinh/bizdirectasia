import selenium
from selenium import webdriver
import json
import time
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
#driver = webdriver.Chrome(chrome_options=chrome_options)
driver = webdriver.Chrome()
driver.get('https://www.bnrs.dti.gov.ph/update-information/switch/others')
time.sleep(30)

def search_pbn(pbn):
    driver.find_element_by_css_selector('#search_form > div.box-body > div > div > div.row > div.col-md-4 > div > select').click()
    driver.find_element_by_css_selector('#search_form > div.box-body > div > div > div.row > div.col-md-4 > div > select > option:nth-child(1)').click()
    driver.find_element_by_css_selector('#input_value').send_keys(pbn)
    driver.find_element_by_css_selector('#search_form > div.box-body > div > div > div.row > div.col-md-8 > div > div > span > button').click()
    return BeautifulSoup(driver.page_source, 'html.parser').find('div', class_='message').get_text()

for i in range(1000000, 10000000):
    print(search_pbn(str(i)))
    time.sleep(2)
