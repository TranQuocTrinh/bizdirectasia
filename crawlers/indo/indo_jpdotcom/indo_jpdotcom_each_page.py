import selenium
from selenium import webdriver
from bs4 import BeautifulSoup
import json
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import sys
import os
from tqdm import tqdm

if not os.path.exists('./data_website_indo_jpdotcom'):
    os.makedirs('./data_website_indo_jpdotcom')

# setting hiden window browser
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome()#chrome_options=chrome_options)
base_url = 'https://www.indonesiayp.com'

input_page = int(sys.argv[1])

def extract_company_name_website(soup):
    data = {}
    try:
        data['website'] = soup.find('div', class_='text weblinks').find('a')['href']
    except:
        return False
    data['company_name'] = soup.find('h1').getText()
    return data

url_cities = json.load(open('./res_cities.json'))

page = input_page
while True:
    remove_url = []
    for url_city in tqdm(url_cities):
        print('city:', url_city.split('/')[-1], '\tpage:', page)
        driver.get(url_city + '/' + str(page))
        time.sleep(10)
        soup_location = BeautifulSoup(driver.page_source, 'html.parser')
        if soup_location.find('h1').get_text() == '404 error: Page not found':
            remove_url.append(url_city)
            print('404 error: Page not found')
        else:
            url_companies = [base_url + x.find('a')['href'] for x in soup_location.findAll('h4')]
            for url_company in tqdm(url_companies):
                driver.get(url_company)
                time.sleep(2)
                data = extract_company_name_website(BeautifulSoup(driver.page_source,'html.parser'))
                if data != False:
                    data['city'] = url_city.split('/')[-1]
                    data['page'] = str(page)
                    json.dump(data, open('data_website_indo_jpdotcom/'+ \
                        str(page) + '_'+ data['city'].lower() + '_' + data['company_name'].lower().replace(' ','_').replace('/','-')+'.json','w'))
                    #print(data)
    page += 1
    for rm_url in remove_url:
        url_cities.remove(rm_url)
    print('res_city is ...', len(url_cities))
    json.dump(url_cities, open('res_cities.json','w'))
    if len(url_cities) == 0:
        print('done!')
        break
