"""
    Wikipedia.org random article scrapper

    @matnesis
    2018/01/07
"""

import json
import os
import re
import sys
import time

import requests
from bs4 import BeautifulSoup

HOME = os.path.normpath(  # The script directory + cxfreeze compatibility
    os.path.dirname(
        sys.executable if getattr(sys, 'frozen', False) else __file__))


def intfalse(nstr):
    """
        Return the int from the string, or False if value error.
    """

    try:
        n = int(nstr)
    except ValueError:
        n = False
    return n


def get_random_wiki(language="en"):
    """
        Return a random Wikipedia article url.
    """

    headers = {
        'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    }

    if language == "es":
        url = "https://es.wikipedia.org/wiki/Especial:Aleatoria"
    else:
        url = "https://en.wikipedia.org/wiki/Special:Random"

    response = requests.get(url, headers=headers)

    if response.history:
        return response.url
    return None


def get_wiki_summary(url):
    """
        Return a dictionary with a summary of a Wikipedia page.
    """

    headers = {
        'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    }
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")

    data = {}

    try:
        title = soup.find('h1', {'id': 'firstHeading'})
        title = title.text if title else False
    except AttributeError:
        title = False

    try:
        description = soup.find('div', {
            'id': 'mw-content-text'
        }).find('div').find(
            'p', recursive=False).text
        description = re.sub('\[[^\[>]+\]', '', description)  # No [1]
    except AttributeError:
        description = False

    try:
        images = soup.find('div', {
            'id': 'mw-content-text'
        }).find_all('img', {
            'srcset': True
        })

        # Extract url from microformat in srcset e.g.
        # '//upload.wikimedia.org/400px-Lernaean_Hydra_Louvre_CA598_n2.jpg 2x'
        images = [
            "https://" + i['srcset'].replace('//', ' ').split()[-2]
            for i in images
        ]

        # Sometimes the size is in the name e.g. '480px-Map_of_USA_SD.svg.png'
        images = {
            img: {
                'size': intfalse(
                    img.replace('/', ' ').split()[-1].split("px")[0])
            }
            for img in images
        }
    except AttributeError:
        images = False

    data[url] = {
        'title': title,
        'description': description,
        'images': images,
        'time': time.time()
    }

    return data


if __name__ == "__main__":

    # Testing

    with open(os.path.join(HOME, "random-en.json"), "w") as f:
        json.dump(get_wiki_summary(get_random_wiki(language="en")), f)

    with open(os.path.join(HOME, "random-es.json"), "w") as f:
        json.dump(get_wiki_summary(get_random_wiki(language="es")), f)

    with open(os.path.join(HOME, "summary.json"), "w") as f:
        json.dump(get_wiki_summary('https://en.wikipedia.org/wiki/Love'), f)
