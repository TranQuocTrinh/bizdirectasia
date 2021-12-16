# README.md
# pip install fuzzywuzzy flair requests bs4 tqdm
# pip install python-Levenshtein pandas
# pip install langdetect

from flair.data import Sentence
from flair.models import TARSTagger
from flair.models import SequenceTagger
from bs4 import BeautifulSoup
import requests
from fuzzywuzzy import process, fuzz
from Levenshtein import distance as levenshtein_distance
import string
import re
from tqdm import tqdm
import json
import os
import pandas as pd
from langdetect import detect, detect_langs

import flair, torch
# flair.device = torch.device('cpu')

CANT_EXTRACT_MESSAGE = "can't extract"
NO_RESPONSE_MESSAGE = "no response"
TIME_OUT_MESSAGE = "timeout"
TIME_RESPONSE = 20
TIME_TOTAL = 60


def create_fair_pretrained():
    tagger = SequenceTagger.load("flair/ner-english-ontonotes-large")
    return tagger


def fair_ner_18classes(tagger, sent):
    sentence = Sentence(sent)
    tagger.predict(sentence)
    tokens = [token.text for token in sentence.tokens]
    tags = ['O'] * len(tokens)
    for entity in sentence.get_spans('ner'):
        label = entity.labels[0].value
        for (i, token) in enumerate(entity.tokens):
            if i == 0:
                tags[token.idx - 1] = f'B-{label}'
            else:
                tags[token.idx - 1] = f'I-{label}'
    return tokens, tags

def convert_tags(tokens, tags):
    entities = []
    word = []
    for i in range(len(tags)):
        tag, token = tags[i], tokens[i]
        if tag[0] == "B":
            if len(word) > 0:
                entities.append((" ".join(word), entity))
            word = [token]
            entity = tag.split("-")[-1]
        elif tag[0] == "I":
            if len(word) > 0:
                word.append(token)
            else:
                print("Something wrong!")
        elif tag[0] == "O":
            if len(word) > 0:
                entities.append((" ".join(word), entity))
                word, entity = [], ""
    
    return entities

def remove_special_characters(text):
    import string
    printable = set(string.printable)
    text = ''.join(filter(lambda x: x in printable, text))
    return text

def check_common_website(company_name):
    commont_web = {"facebook", "linkedin", "youtube", "alibaba", "twitter", "godaddy", "namebright", "yellow"}
    return company_name.lower() in commont_web

def similariry_string(s1, s2):
    def preprocess(text):
        text = str(text).lower()
        text = text.replace("https://", "").replace("http://", "").replace("www.", "")
        text = text.split(".")
        if len(text) > 1:
            text = ".".join(text[:-1])
        else:
            text = ".".join(text)

        text = re.sub(r'[^\x00-\x7F]+','', text)
        return text

    s1 = preprocess(s1)
    s2 = preprocess(s2)
    fuz_score = fuzz.token_set_ratio(s1, s2)/100
    try:
        lev_score = (1-levenshtein_distance(s1, s2)/max(len(s1), len(s2)))
    except:
        lev_score = 0
    return (fuz_score + lev_score)/2


def frequency_score(lst_company_name_candidates):
    from collections import Counter
    count = Counter(lst_company_name_candidates)
    return {candi:count[candi]/len(lst_company_name_candidates) for candi in lst_company_name_candidates}


def confidence_score(lst_company_name_candidates):
    score_similar_candidates = {candi: similariry_string(website, candi) for candi in set(lst_company_name_candidates)}
    score_freq_candidates = frequency_score(lst_company_name_candidates)
    scores = []
    for candi in score_similar_candidates:
        sc = (2*score_similar_candidates[candi]+score_freq_candidates[candi])/3
        scores.append((candi, sc))
    return scores


def extract_main(tagger, text):
    tokens, tags = fair_ner_18classes(
        tagger,
        text
    )
    entities = convert_tags(tokens, tags)
    company_name_candidates = [text for text,entity in entities if entity in {"ORG"}]
    company_name_candidates = confidence_score(company_name_candidates)
    company_name_candidates = sorted(company_name_candidates, key=lambda x: x[1], reverse=True)
    company_name_candidates = [candi for candi in company_name_candidates if not check_common_website(candi[0])]
    company_name = company_name_candidates[0][0] if len(company_name_candidates) > 0 else CANT_EXTRACT_MESSAGE

    gpe_candidates = [text for text,entity in entities if entity in {"GPE"}]
    address_candidates = [text for text in gpe_candidates if len(text.split(" ")) > 5]
    address = address_candidates[0] if len(address_candidates) > 0 else CANT_EXTRACT_MESSAGE
    
    if address != CANT_EXTRACT_MESSAGE:
        country = address # need more process
    elif len(set(gpe_candidates)) == 1:
        country = gpe_candidates[0]
    else:
        country = CANT_EXTRACT_MESSAGE

    return company_name, country, address


def extract_country_from_domain(website):
    # from domain
    dct = {
        '.ac': 'Ascension Island (United Kingdom)',
        '.ad': 'Andorra',
        '.ae': 'United Arab Emirates',
        '.af': 'Afghanistan',
        '.ag': 'Antigua and Barbuda',
        '.ai': 'Anguilla (United Kingdom)',
        '.al': 'Albania',
        '.am': 'Armenia',
        '.ao': 'Angola',
        '.aq': 'Antarctica',
        '.ar': 'Argentina',
        '.as': 'American Samoa (United States)',
        '.at': 'Austria',
        '.au': 'Australia',
        '.aw': 'Aruba (Kingdom of the Netherlands)',
        '.ax': 'Åland (Finland)',
        '.az': 'Azerbaijan',
        '.ba': 'Bosnia and Herzegovina',
        '.bb': 'Barbados',
        '.bd': 'Bangladesh',
        '.be': 'Belgium',
        '.bf': 'Burkina Faso',
        '.bg': 'Bulgaria',
        '.bh': 'Bahrain',
        '.bi': 'Burundi',
        '.bj': 'Benin',
        '.bm': 'Bermuda (United Kingdom)',
        '.bn': 'Brunei',
        '.bo': 'Bolivia',
        '.bq': 'Caribbean Netherlands ( Bonaire,  Saba, and  Sint Eustatius)',
        '.br': 'Brazil',
        '.bs': 'Bahamas',
        '.bt': 'Bhutan',
        '.bw': 'Botswana',
        '.by': 'Belarus',
        '.bz': 'Belize',
        '.ca': 'Canada',
        '.cc': 'Cocos (Keeling) Islands',
        '.cd': 'Democratic Republic of the Congo',
        '.cf': 'Central African Republic',
        '.cg': 'Republic of the Congo',
        '.ch': 'Switzerland',
        '.ci': 'Ivory Coast',
        '.ck': 'Cook Islands',
        '.cl': 'Chile',
        '.cm': 'Cameroon',
        '.cn': "People's Republic of China",
        '.cr': 'Costa Rica',
        '.cu': 'Cuba',
        '.cv': 'Cape Verde',
        '.cw': 'Curaçao (Kingdom of the Netherlands)',
        '.cx': 'Christmas Island',
        '.cy': 'Cyprus',
        '.cz': 'Czech Republic',
        '.de': 'Germany',
        '.dj': 'Djibouti',
        '.dk': 'Denmark',
        '.dm': 'Dominica',
        '.do': 'Dominican Republic',
        '.dz': 'Algeria',
        '.ec': 'Ecuador',
        '.ee': 'Estonia',
        '.eg': 'Egypt',
        '.eh': 'Western Sahara',
        '.er': 'Eritrea',
        '.es': 'Spain',
        '.et': 'Ethiopia',
        '.eu': 'European Union',
        '.fi': 'Finland',
        '.fj': 'Fiji',
        '.fk': 'Falkland Islands (United Kingdom)',
        '.fm': 'Federated States of Micronesia',
        '.fo': 'Faroe Islands (Kingdom of Denmark)',
        '.fr': 'France',
        '.ga': 'Gabon',
        '.gd': 'Grenada',
        '.ge': 'Georgia',
        '.gf': 'French Guiana (France)',
        '.gg': 'Guernsey',
        '.gh': 'Ghana',
        '.gi': 'Gibraltar (United Kingdom)',
        '.gl': 'Greenland (Kingdom of Denmark)',
        '.gm': 'The Gambia',
        '.gn': 'Guinea',
        '.gp': 'Guadeloupe (France)',
        '.gq': 'Equatorial Guinea',
        '.gr': 'Greece',
        '.gs': 'South Georgia and the South Sandwich Islands (United Kingdom)',
        '.gt': 'Guatemala',
        '.gu': 'Guam (United States)',
        '.gw': 'Guinea-Bissau',
        '.gy': 'Guyana',
        '.hk': 'Hong Kong',
        '.hm': 'Heard Island and McDonald Islands',
        '.hn': 'Honduras',
        '.hr': 'Croatia',
        '.ht': 'Haiti',
        '.hu': 'Hungary',
        '.id': 'Indonesia',
        '.ie': 'Ireland',
        '.il': 'Israel',
        '.im': 'Isle of Man',
        '.in': 'India',
        '.io': 'British Indian Ocean Territory (United Kingdom)',
        '.iq': 'Iraq',
        '.ir': 'Iran',
        '.is': 'Iceland',
        '.it': 'Italy',
        '.je': 'Jersey',
        '.jm': 'Jamaica',
        '.jo': 'Jordan',
        '.jp': 'Japan',
        '.ke': 'Kenya',
        '.kg': 'Kyrgyzstan',
        '.kh': 'Cambodia',
        '.ki': 'Kiribati',
        '.km': 'Comoros',
        '.kn': 'Saint Kitts and Nevis',
        '.kp': 'North Korea',
        '.kr': 'South Korea',
        '.kw': 'Kuwait',
        '.ky': 'Cayman Islands (United Kingdom)',
        '.kz': 'Kazakhstan',
        '.la': 'Laos',
        '.lb': 'Lebanon',
        '.lc': 'Saint Lucia',
        '.li': 'Liechtenstein',
        '.lk': 'Sri Lanka',
        '.lr': 'Liberia',
        '.ls': 'Lesotho',
        '.lt': 'Lithuania',
        '.lu': 'Luxembourg',
        '.lv': 'Latvia',
        '.ly': 'Libya',
        '.ma': 'Morocco',
        '.mc': 'Monaco',
        '.md': 'Moldova',
        '.me': 'Montenegro',
        '.mg': 'Madagascar',
        '.mh': 'Marshall Islands',
        '.mk': 'North Macedonia',
        '.ml': 'Mali',
        '.mm': 'Myanmar',
        '.mn': 'Mongolia',
        '.mo': 'Macau',
        '.mp': 'Northern Mariana Islands (United States)',
        '.mq': 'Martinique (France)',
        '.mr': 'Mauritania',
        '.ms': 'Montserrat (United Kingdom)',
        '.mt': 'Malta',
        '.mu': 'Mauritius',
        '.mv': 'Maldives',
        '.mw': 'Malawi',
        '.mx': 'Mexico',
        '.my': 'Malaysia',
        '.mz': 'Mozambique',
        '.na': 'Namibia',
        '.nc': 'New Caledonia (France)',
        '.ne': 'Niger',
        '.nf': 'Norfolk Island',
        '.ng': 'Nigeria',
        '.ni': 'Nicaragua',
        '.nl': 'Netherlands',
        '.no': 'Norway',
        '.np': 'Nepal',
        '.nr': 'Nauru',
        '.nu': 'Niue',
        '.nz': 'New Zealand',
        '.om': 'Oman',
        '.pa': 'Panama',
        '.pe': 'Peru',
        '.pf': 'French Polynesia (France)',
        '.pg': 'Papua New Guinea',
        '.ph': 'Philippines',
        '.pk': 'Pakistan',
        '.pl': 'Poland',
        '.pm': 'Saint-Pierre and Miquelon (France)',
        '.pn': 'Pitcairn Islands (United Kingdom)',
        '.pr': 'Puerto Rico (United States)',
        '.ps': 'Palestine[56]',
        '.pt': 'Portugal',
        '.pw': 'Palau',
        '.py': 'Paraguay',
        '.qa': 'Qatar',
        '.re': 'Réunion (France)',
        '.ro': 'Romania',
        '.rs': 'Serbia',
        '.ru': 'Russia',
        '.rw': 'Rwanda',
        '.sa': 'Saudi Arabia',
        '.sb': 'Solomon Islands',
        '.sc': 'Seychelles',
        '.sd': 'Sudan',
        '.se': 'Sweden',
        '.sg': 'Singapore',
        '.sh': 'Saint Helena, Ascension and Tristan da Cunha (United Kingdom)',
        '.si': 'Slovenia',
        '.sk': 'Slovakia',
        '.sl': 'Sierra Leone',
        '.sm': 'San Marino',
        '.sn': 'Senegal',
        '.so': 'Somalia',
        '.sr': 'Suriname',
        '.ss': 'South Sudan',
        '.st': 'São Tomé and Príncipe',
        '.su': 'Soviet Union',
        '.sv': 'El Salvador',
        '.sx': 'Sint Maarten (Kingdom of the Netherlands)',
        '.sy': 'Syria',
        '.sz': 'Eswatini',
        '.tc': 'Turks and Caicos Islands (United Kingdom)',
        '.td': 'Chad',
        '.tf': 'French Southern and Antarctic Lands',
        '.tg': 'Togo',
        '.th': 'Thailand',
        '.tj': 'Tajikistan',
        '.tk': 'Tokelau',
        '.tl': 'East Timor',
        '.tm': 'Turkmenistan',
        '.tn': 'Tunisia',
        '.to': 'Tonga',
        '.tr': 'Turkey',
        '.tt': 'Trinidad and Tobago',
        '.tv': 'Tuvalu',
        '.tw': 'Taiwan',
        '.tz': 'Tanzania',
        '.ua': 'Ukraine',
        '.ug': 'Uganda',
        '.uk': 'United Kingdom',
        '.us': 'United States of America',
        '.uy': 'Uruguay',
        '.uz': 'Uzbekistan',
        '.va': 'Vatican City',
        '.vc': 'Saint Vincent and the Grenadines',
        '.ve': 'Venezuela',
        '.vg': 'British Virgin Islands (United Kingdom)',
        '.vi': 'United States Virgin Islands (United States)',
        '.vn': 'Vietnam',
        '.vu': 'Vanuatu',
        '.wf': 'Wallis and Futuna',
        '.ws': 'Samoa',
        '.ye': 'Yemen',
        '.yt': 'Mayotte',
        '.za': 'South Africa',
        '.zm': 'Zambia',
        '.zw': 'Zimbabwe'
        }
    web_split = website.split("/")
    if "http:" in web_split or "https:" in web_split:
        dot = "." + "/".join(web_split[:3]).split(".")[-1]
    else:
        dot = "." + web_split[0].split(".")[-1]

    return dct.get(dot, None)

def extract_country_by_detect_language(text):
    code = detect(text)
    dct = {
        'ab': 'Abkhazian',
        'aa': 'Afar',
        'af': 'Afrikaans',
        'ak': 'Akan',
        'sq': 'Albanian',
        'am': 'Amharic',
        'ar': 'Arabic',
        'an': 'Aragonese',
        'hy': 'Armenian',
        'as': 'Assamese',
        'av': 'Avaric',
        'ae': 'Avestan',
        'ay': 'Aymara',
        'az': 'Azerbaijani',
        'bm': 'Bambara',
        'ba': 'Bashkir',
        'eu': 'Basque',
        'be': 'Belarusian',
        'bn': 'Bengali',
        'bi': 'Bislama',
        'bs': 'Bosnian',
        'br': 'Breton',
        'bg': 'Bulgarian',
        'my': 'Burmese',
        'ca': 'Catalan, Valencian',
        'km': 'Central Khmer',
        'ch': 'Chamorro',
        'ce': 'Chechen',
        'ny': 'Chichewa, Chewa, Nyanja',
        'zh': 'Chinese',
        'cu': 'Church Slavic, Old Slavonic, Church Slavonic, Old Bulgarian, Old Church Slavonic',
        'cv': 'Chuvash',
        'kw': 'Cornish',
        'co': 'Corsican',
        'cr': 'Cree',
        'hr': 'Croatian',
        'cs': 'Czech',
        'da': 'Danish',
        'dv': 'Divehi, Dhivehi, Maldivian',
        'nl': 'Dutch, Flemish',
        'dz': 'Dzongkha',
        'en': 'English',
        'eo': 'Esperanto',
        'et': 'Estonian',
        'ee': 'Ewe',
        'fo': 'Faroese',
        'fj': 'Fijian',
        'fi': 'Finnish',
        'fr': 'French',
        'ff': 'Fulah',
        'gd': 'Gaelic, Scottish Gaelic',
        'gl': 'Galician',
        'lg': 'Ganda',
        'ka': 'Georgian',
        'de': 'German',
        'el': 'Greek, Modern (1453–)',
        'gn': 'Guarani',
        'gu': 'Gujarati',
        'ht': 'Haitian, Haitian Creole',
        'ha': 'Hausa',
        'he': 'Hebrew',
        'hz': 'Herero',
        'hi': 'Hindi',
        'ho': 'Hiri Motu',
        'hu': 'Hungarian',
        'is': 'Icelandic',
        'io': 'Ido',
        'ig': 'Igbo',
        'id': 'Indonesian',
        'ia': 'Interlingua (International Auxiliary Language Association)',
        'ie': 'Interlingue, Occidental',
        'iu': 'Inuktitut',
        'ik': 'Inupiaq',
        'ga': 'Irish',
        'it': 'Italian',
        'ja': 'Japanese',
        'jv': 'Javanese',
        'kl': 'Kalaallisut, Greenlandic',
        'kn': 'Kannada',
        'kr': 'Kanuri',
        'ks': 'Kashmiri',
        'kk': 'Kazakh',
        'ki': 'Kikuyu, Gikuyu',
        'rw': 'Kinyarwanda',
        'ky': 'Kirghiz, Kyrgyz',
        'kv': 'Komi',
        'kg': 'Kongo',
        'ko': 'Korean',
        'kj': 'Kuanyama, Kwanyama',
        'ku': 'Kurdish',
        'lo': 'Lao',
        'la': 'Latin',
        'lv': 'Latvian',
        'li': 'Limburgan, Limburger, Limburgish',
        'ln': 'Lingala',
        'lt': 'Lithuanian',
        'lu': 'Luba-Katanga',
        'lb': 'Luxembourgish, Letzeburgesch',
        'mk': 'Macedonian',
        'mg': 'Malagasy',
        'ms': 'Malay',
        'ml': 'Malayalam',
        'mt': 'Maltese',
        'gv': 'Manx',
        'mi': 'Maori',
        'mr': 'Marathi',
        'mh': 'Marshallese',
        'mn': 'Mongolian',
        'na': 'Nauru',
        'nv': 'Navajo, Navaho',
        'ng': 'Ndonga',
        'ne': 'Nepali',
        'nd': 'North Ndebele',
        'se': 'Northern Sami',
        'no': 'Norwegian',
        'nb': 'Norwegian Bokmål',
        'nn': 'Norwegian Nynorsk',
        'oc': 'Occitan',
        'oj': 'Ojibwa',
        'or': 'Oriya',
        'om': 'Oromo',
        'os': 'Ossetian, Ossetic',
        'pi': 'Pali',
        'ps': 'Pashto, Pushto',
        'fa': 'Persian',
        'pl': 'Polish',
        'pt': 'Portuguese',
        'pa': 'Punjabi, Panjabi',
        'qu': 'Quechua',
        'ro': 'Romanian, Moldavian, Moldovan',
        'rm': 'Romansh',
        'rn': 'Rundi',
        'ru': 'Russian',
        'sm': 'Samoan',
        'sg': 'Sango',
        'sa': 'Sanskrit',
        'sc': 'Sardinian',
        'sr': 'Serbian',
        'sn': 'Shona',
        'ii': 'Sichuan Yi, Nuosu',
        'sd': 'Sindhi',
        'si': 'Sinhala, Sinhalese',
        'sk': 'Slovak',
        'sl': 'Slovenian',
        'so': 'Somali',
        'nr': 'South Ndebele',
        'st': 'Southern Sotho',
        'es': 'Spanish, Castilian',
        'su': 'Sundanese',
        'sw': 'Swahili',
        'ss': 'Swati',
        'sv': 'Swedish',
        'tl': 'Tagalog',
        'ty': 'Tahitian',
        'tg': 'Tajik',
        'ta': 'Tamil',
        'tt': 'Tatar',
        'te': 'Telugu',
        'th': 'Thai',
        'bo': 'Tibetan',
        'ti': 'Tigrinya',
        'to': 'Tonga (Tonga Islands)',
        'ts': 'Tsonga',
        'tn': 'Tswana',
        'tr': 'Turkish',
        'tk': 'Turkmen',
        'tw': 'Twi',
        'ug': 'Uighur, Uyghur',
        'uk': 'Ukrainian',
        'ur': 'Urdu',
        'uz': 'Uzbek',
        've': 'Venda',
        'vi': 'Vietnamese',
        'vo': 'Volapük',
        'wa': 'Walloon',
        'cy': 'Welsh',
        'fy': 'Western Frisian',
        'wo': 'Wolof',
        'xh': 'Xhosa',
        'yi': 'Yiddish',
        'yo': 'Yoruba',
        'za': 'Zhuang, Chuang',
        'zu': 'Zulu'}
    return dct[code] if code != "en" else None

def get_text_from_url(url):
    if url.split("/")[0] not in {"http:", "https"}:
        try:
            response = requests.get("http://"+url, timeout=TIME_RESPONSE)
            text = " ".join(BeautifulSoup(response.text, "html.parser").getText().split())
            return text
        except:
            pass
        
        try:
            response = requests.get("https://"+url, timeout=TIME_RESPONSE)
            text = " ".join(BeautifulSoup(response.text, "html.parser").getText().split())
            return text
        except:
            return None
    else:
        try:
            response = requests.get(url, timeout=TIME_RESPONSE)
            text = " ".join(BeautifulSoup(response.text, "html.parser").getText().split())
            return text
        except:
            return None


def extract_company_name_country_address(tagger, website, text):
    country = extract_country_from_domain(website)
    if text == "":
        country = NO_RESPONSE_MESSAGE if country is None else country
        company_name, address = NO_RESPONSE_MESSAGE, NO_RESPONSE_MESSAGE
    else:
        company_name, country_ext, address = extract_main(tagger, text)
        country = country_ext if country is None else country

    return company_name, country, address


import signal
def handler(signum, frame):
    raise Exception(TIME_OUT_MESSAGE)
signal.signal(signal.SIGALRM, handler)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_thread", default=1, type=int, required=False, help="Number of thread for task",)
    parser.add_argument("--thread", default=0, type=int,required=False, help="Thread id for split data runing",)
    parser.add_argument("--cache_text_dir", default="cache_text/", type=str,required=False, help="Directory of cache text",)
    parser.add_argument("--cache_extract_dir", default="cache_extract/", type=str,required=False, help="Directory of cache extract",)
    parser.add_argument("--output_csv_path", default="enrich_newzealand.csv", type=str,required=False, help="Path of output csv file",)
    args = parser.parse_args()

    if not os.path.exists(args.cache_extract_dir):
        os.makedirs(args.cache_extract_dir)
    # lst_domain = [x for x in open("newzealand.txt").read().split("\n") if x]
    
    # number_samples = len(lst_domain)//int(args.num_thread)
    # from_idx = number_samples * int(args.thread)
    # if int(args.thread) == int(args.num_thread)-1:
    #     to_idx = len(lst_domain)
    # else:
    #     to_idx = number_samples*(int(args.thread)+1)
    # lst_domain = lst_domain[from_idx:to_idx]

    df, error = [], []
    for f in os.listdir(args.cache_text_dir):
        try:
            df.append(json.load(open(os.path.join(args.cache_text_dir, f))))
        except:
            error.append(os.path.join(args.cache_text_dir, f))
    df = pd.DataFrame(df)
    print("Work:", df.shape, "error:", len(error))

    tagger = create_fair_pretrained()
    # df = get_data_es(size=1000)
    bar = tqdm(df.iterrows(), total=df.shape[0], desc="Extract...")
    lst_company_extract, lst_country_extract, lst_address_extract = [], [], []
    count_company_name, count_country, count_address = 0, 0, 0
    for i,r in bar:
        website = r["website"]
        text = r["text"] if len(r["text"]) < 4096 else r["text"][:4096]
        fpath = f"{args.cache_extract_dir}{website.replace('/', '-')}.json"
        if os.path.exists(fpath):
            res = json.load(open(fpath))
            company_name, country, address = res["company_name_extract"], res["country_extract"], res["address_extract"]
        else:
            try:
                signal.alarm(TIME_TOTAL)
                company_name, country, address = extract_company_name_country_address(tagger, website, text)
                company_name = remove_special_characters(company_name)
                signal.alarm(0)
            except Exception as exc:
                company_name, country, address = TIME_OUT_MESSAGE, TIME_OUT_MESSAGE, TIME_OUT_MESSAGE
            res = dict(website=website, company_name_extract=company_name, country_extract=country, address_extract=address)
            json.dump(res, open(fpath, "w"))


        if company_name not in {NO_RESPONSE_MESSAGE, CANT_EXTRACT_MESSAGE, TIME_OUT_MESSAGE, None, ""}:
            count_company_name += 1
        if country not in {NO_RESPONSE_MESSAGE, CANT_EXTRACT_MESSAGE, TIME_OUT_MESSAGE, None, ""}:
            count_country += 1
        if address not in {NO_RESPONSE_MESSAGE, CANT_EXTRACT_MESSAGE, TIME_OUT_MESSAGE, None, ""}:
            count_address += 1
        bar.set_postfix(company_name=count_company_name)
        
        # print(json.dumps(res, indent=4))
        # print("-"*70)
        lst_company_extract.append(company_name)
        lst_country_extract.append(country)
        lst_address_extract.append(address)
        

    df["company_name_extract"] = lst_company_extract
    df["country_extract"] = lst_country_extract
    df["address_extract"] = lst_address_extract

    # filter and to_csv
    idx = [i for i,r in df.iterrows() if r["company_name_extract"] not in {NO_RESPONSE_MESSAGE, CANT_EXTRACT_MESSAGE, TIME_OUT_MESSAGE, None, ""}]
    df = df.loc[idx, ].reset_index(drop=True)
    df = df[["website", "text", "company_name_extract", "country_extract", "address_extract"]]
    print(f"Final extract report: \ndf.shape: {df.shape}")
    
    def remove_non_ascii(text):
        import string
        printable = set(string.printable)
        return ''.join(filter(lambda x: x in printable, text))
    for col in ["text", "company_name_extract", "country_extract", "address_extract"]:
        df[col] = df[col].apply(remove_non_ascii)

    df.to_csv(args.output_csv_path, index=False)