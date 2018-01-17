"""
    Wikipedia API wrapper for random articles and images.
"""

import json
import os
import sys
import requests

HOME = os.path.normpath(  # The script directory + cxfreeze compatibility
    os.path.dirname(
        sys.executable if getattr(sys, 'frozen', False) else __file__))


def get_random_articles(count=1, lang="en"):
    """
        Return a json with random articles from Wikipedia API. It includes id,
        title, summary and main image when available.
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


def get_random_articles_with_images():
    pass


if __name__ == "__main__":

    # Tests

    with open(os.path.join(HOME, "sample-random-articles.json"), 'w') as f:
        json.dump(get_random_articles(count=10), f)

    with open(os.path.join(HOME, "sample-image-info.json"), 'w') as f:
        json.dump(get_image_info("USA_Wisconsin_location_map.svg"), f)
