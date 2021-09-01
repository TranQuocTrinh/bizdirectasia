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

if not os.path.exists('./data_website_korea_jpdotcom'):
    os.makedirs('./data_website_korea_jpdotcom')

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

dct_cate = json.load(open('./res_dct_cate_korea.json'))

page = input_page
while True:
    for cate_lv_1 in dct_cate:
        remove_url = {k:[] for k in dct_cate}
        for ob_js in dct_cate[cate_lv_1]:
            cate_lv_2 = list(ob_js.keys())[0]
            url_cate = list(ob_js.values())[0]

            print('category:', url_cate.split('/')[-1], '\tpage:', page)
            driver.get(url_cate + '/' + str(page))
            time.sleep(10)
            soup_location = BeautifulSoup(driver.page_source, 'html.parser')
            if soup_location.find('h1').get_text() == '404 error: Page not found':
                remove_url[cate_lv_1].append(ob_js)
                print('404 error: Page not found')
            else:
                url_companies = [base_url + x.find('a')['href'] for x in soup_location.findAll('h4')]

                temp = 0
                for url_company in tqdm(range(4, len(url_companies) + 4)):
                    css_selector = '#listings > div:nth-child(' +str(url_company)+') > h4 > a'
                    count_click_1 = 0
                    while True:
                        try:
                            driver.find_element_by_css_selector(css_selector).click()
                            count_click_1 = 0
                            break
                        except:
                            count_click_1 += 1
                            if count_click_1 > 20:
                                break
                            pass
                    if temp != 0 or count_click_1 > 20:
                        css_selector = '#cmap_'+ str(temp) +' > h4 > a'
                        count_click_2 = 0
                        while True:
                            try:
                                driver.find_element_by_css_selector(css_selector).click()
                                count_click_2 = 0
                                temp += 1
                                break
                            except:
                                count_click_2 += 1
                                if count_click_2 > 20:
                                    print('FALSE !!!')
                                    exit()
                                pass

                    time.sleep(1.5)
                    data = extract_company_name_website(BeautifulSoup(driver.page_source,'html.parser'))
                    if data != False:
                        data['category_level1'] = cate_lv_1
                        data['category_level2'] = cate_lv_2
                        data['page'] = str(page)
                        file_name = 'data_website_korea_jpdotcom/'+ str(page) + '_' \
                                + cate_lv_1.lower().replace(' ','_').replace('/','-')+ '_' \
                                + cate_lv_2.lower().replace(' ','_').replace('/','-') + '_' \
                                + data['company_name'].lower().replace(' ','_').replace('/','-')+'.json'
                        json.dump(data, open(file_name ,'w'))
                        print(data)
                    driver.execute_script("window.history.go(-1)")
                    time.sleep(0.75)
    page += 1
    for k in remove_url:
        for ob in remove_url[k]:
            dct_cate[k].remove(ob)
    leng = 0
    for cate1 in dct_cate:
        leng += len(dct_cate[cate1])
    json.dump(dct_cate, open('res_dct_cate_korea.json','w'))
    if leng == 0:
        print('done!')
        break
