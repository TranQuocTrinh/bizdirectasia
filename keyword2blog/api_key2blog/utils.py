import string
import re


def clean_text(text):
    text = text.lower()
    text = re.sub('\[.*?\]', ' ', text)
    text = re.sub('\[[^>]+\]', ' ', text)

    text = re.sub('\(.*?\)', ' ', text)
    text = re.sub('\([^>]+\)', ' ', text)

    text = re.sub('\{.*?\}', ' ', text)
    text = re.sub('\{[^>]+\}', ' ', text)

    text = re.sub('<[^>]+>', ' ', text)
    text = re.sub('<[^>]+>', ' ', text)

    printable = set(string.printable)
    text = ''.join(filter(lambda x: x in printable, text))
    text = ' '.join(text.split())
    return text
