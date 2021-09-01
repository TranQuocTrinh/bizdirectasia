from selenium import webdriver
from bs4 import BeautifulSoup
import time
import pandas as pd
from tqdm import tqdm
import json
import os


def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument("disable-gpu")

    driver = webdriver.Chrome(options=options)
    url = f"https://app.apollo.io/"
    driver.get(url)
    time.sleep(1)
    return driver


def login(driver):
    driver.find_element_by_css_selector(
        "#o3-input").send_keys("dien.tran@bizdirectasia.com")
    driver.find_element_by_css_selector(
        "#o4-input").send_keys("Saigon456$%^\n")
    time.sleep(1)
    return driver


def search(driver, website="www.vingroup.net"):
    url = f"https://app.apollo.io/#/companies?finderViewId=5a205be49a57e40c095e1d60&page=1&qOrganizationName={website}"
    driver.get(url)
    time.sleep(1)


def extract_list_company(soup):
    pass


def extract_description_keywords(soup):
    description, keywords = '', []
    for div in soup.findAll("div", class_="zp_1j8_V"):
        if div.getText() == "Description":
            description = div.find_parent().getText()
        if div.getText() == "Keywords":
            keywords = [x.getText() for x in div.find_parent().findAll("div")]
    if len(keywords) > 0:
        keywords = keywords[2:]
    keywords = list(set(keywords))

    if description != "":
        description = description[11:-10]
    return description, keywords


def main():
    import sys
    df = pd.read_csv("des_web_aus.csv")
    if len(sys.argv) == 3:
        split = int(sys.argv[1])
        thread = int(sys.argv[2])
        start, end = int(df.shape[0]/split *
                         thread), int(df.shape[0]/split*(thread+1))
        print(start, end, df.shape[0]/split)
        df = df[start:end]

    driver = create_driver()
    login(driver)

    bar = tqdm(df.iterrows(), total=df.shape[0])
    description_apollo, keywords_apollo = [], []
    for i, r in bar:
        website = r["website"]
        website = ''.join([x for x in website.split('/')[1:] if x])
        cache_file_path = f"cache/{website}.json"
        if os.path.exists(cache_file_path):
            cache = json.load(open(cache_file_path))
            des, keywords = cache["description"], cache["keywords"]
        else:
            des, keywords = '', []
            search(driver, website)
            try:
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                tbody = soup.find("table").find("tbody")
                if tbody != None:
                    url = "https://app.apollo.io/" + tbody.find("a")["href"]
                    driver.get(url)
                    time.sleep(2)
                    driver.find_element_by_css_selector(
                        "#insights_card > div > div.zp_1SyEI > div > div.react-grid-layout.zp_3QXl2 > div:nth-child(1) > div > div > div > div > div > form > div:nth-child(2) > div.zp_2MBpP > div.zp_U7upS > div > div > span > a").click()
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    des, keywords = extract_description_keywords(soup)
            except:
                des, keywords = '', []

            json.dump({"description": des, "keywords": keywords},
                      open(cache_file_path, "w"))
        description_apollo.append(des)
        keywords_apollo.append(keywords)
    df["description_apollo"] = description_apollo
    df["keywords_apollo"] = keywords_apollo
    df.to_csv("crawl.csv")


if __name__ == "__main__":
    main()
