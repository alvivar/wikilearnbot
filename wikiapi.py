"""
    Wikipedia API wrapper for random articles and images.

    @matnesis
    2018/01/17
"""

import json
import os
import sys
import time
import urllib

import requests

HOME = os.path.normpath(  # The script directory + cxfreeze compatibility
    os.path.dirname(
        sys.executable if getattr(sys, 'frozen', False) else __file__))


def get_random_articles(count=1, lang='en'):
    """
        Return a json with random articles from Wikipedia API. It includes
        'pageid', 'title', 'extract' and 'pageimage' when available.
    """

    response = requests.get(
        f"https://{lang}.wikipedia.org/w/api.php",
        params={
            'action': 'query',
            'formatversion': '2',
            'format': 'json',
            'generator': 'random',
            'grnlimit': count,
            'grnnamespace': 0,
            'prop': 'extracts|pageimages',
            'exintro': True,
            'explaintext': True
        },
        headers={
            'User-Agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
        })

    return response.json()


def get_image_info(imagename):
    """
        Return a json with the image info from Wikipedia API.
    """

    response = requests.get(
        f"https://en.wikipedia.org/w/api.php",
        params={
            'action': 'query',
            'formatversion': '2',
            'format': 'json',
            'prop': 'imageinfo',
            'titles': f"File:{imagename}",
            'iiprop': 'url'
        },
        headers={
            'User-Agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
        })

    return response.json()


def get_image_url(imagename):
    """
        Return the url from the Wikipedia image.
    """
    info = get_image_info(imagename)
    return info['query']['pages'][0]['imageinfo'][0]['url']  # Optimism +1


def get_random_articles_with_images(count=1, lang='en', rest=5, ignoreids=[]):
    """
        Return a json file with a list of random articles that always contain a
        main image.

        Even when this function uses Wikipedia API below, the json returned is
        cleaner and compact that a normal Wikipedia response.
    """

    # Filtering only with images

    withimages = []
    while len(withimages) < count:
        ranart = get_random_articles(count=count, lang=lang)
        withimages += [d for d in ranart['query']['pages'] if 'pageimage' in d]
        time.sleep(rest)  # Decent +1

    # A simpler json response, including images urls

    result = []
    for w in withimages:
        title = urllib.parse.quote_plus(w['title'].replace(' ', '_'))
        result.append({
            'pageid': w['pageid'],
            'pageurl': f"https://{lang}.wikipedia.org/wiki/{title}",
            'title': w['title'],
            'extract': w['extract'],
            'pageimage': w['pageimage'],
            'pageimageurl': get_image_url(w['pageimage'])
        })

    return result[:count]


if __name__ == "__main__":

    # Tests

    with open(os.path.join(HOME, "sample-random-articles.json"), 'w') as f:
        json.dump(get_random_articles(count=5), f)

    with open(os.path.join(HOME, "sample-image-info.json"), 'w') as f:
        json.dump(get_image_info("USA_Wisconsin_location_map.svg"), f)

    with open(os.path.join(HOME, "sample-random-articles-images.json"),
              'w') as f:
        json.dump(get_random_articles_with_images(5), f)
