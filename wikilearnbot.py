"""
    Queues Wikipedia articles with images on qbot.json as available.

    @matnesis
    2018/01/08
"""

import json
import os
import random
import shutil
import sys
import time
from urllib.request import urlopen

from wikiscrapper import get_random_wiki, get_wiki_summary

HOME = os.path.normpath(  # The script directory + cxfreeze compatibility
    os.path.dirname(
        sys.executable if getattr(sys, 'frozen', False) else __file__))


def get_random_wikis(count, lang="en", wait=4):
    """
        Return a list with Wikipedia articles dictionaries that contains images.
    """
    wikis = []
    print(f"Looking for {count} random Wikipedia articles...")
    while count > 0:
        wiki = get_wiki_summary(
            get_random_wiki(language=lang), minimgsize=250, incfalseimg=True)

        url = list(wiki.keys())[0]
        imgs = list(wiki.values())[0]['images']
        if imgs:
            print(f"Found #{count} '{url}'")
            wikis.append(wiki)
            count -= 1
        else:
            print(f"Discarded, no images '{url}'")

        time.sleep(random.uniform(wait - 1, wait + 1))

    return wikis


if __name__ == "__main__":

    DELTA = time.time()
    print("@wikilearnbot\n")

    QBOTJSON = os.path.join(HOME, "qbot.json")
    try:
        QBOT = json.load(open(QBOTJSON, "r"))
    except (IOError, ValueError):
        QBOT = {
            "options": {
                "refresh_schedule": True
            },
            "schedule": {
                "name":
                "wikilearnbot",
                "days": [
                    "monday", "tuesday", "wednesday", "thursday", "friday",
                    "saturday", "sunday"
                ],
                "hours": ["8:00", "11:00", "14:00", "17:00", "20:00", "23:00"]
            },
            "twitter_tokens": {
                "consumer_key": "find",
                "consumer_secret": "them",
                "oauth_token": "on",
                "oauth_secret": "apps.twitter.com"
            },
            "messages": []
        }

    # Download wikis, one per schedule

    NEEDED = len(QBOT['schedule']['hours'])
    WIKIS = get_random_wikis(NEEDED)

    WIKISPATH = os.path.join(HOME, "wikis")
    if not os.path.exists(WIKISPATH):
        os.makedirs(WIKISPATH)

    with open(os.path.join(WIKISPATH, f"{round(time.time())}.json"), 'w') as f:
        json.dump(WIKIS, f)

    # Prepare messages and Download images

    TWEETS = []

    IMGPATH = os.path.join(HOME, "images")
    if not os.path.exists(IMGPATH):
        os.makedirs(IMGPATH)

    print("Downloading images...")
    for wiki in WIKIS:
        for urlkey, val in wiki.items():

            # Images
            for imgkey, _ in val['images'].items():
                imgfile = os.path.join(IMGPATH, os.path.basename(imgkey))
                with urlopen(imgkey) as r, open(imgfile, 'wb') as f:
                    shutil.copyfileobj(r, f)
                    print(f"Downloaded '{imgfile}'")
                break  # Just one image

            # Tweets
            desc = val['description']
            desc = desc if len(desc) < 250 else f"{desc[:250]}[...]"

            TWEETS.append({'text': f"{desc} {urlkey}", 'image': imgfile})

    # Qbot queue
    QBOT['messages'] = QBOT['messages'] + TWEETS

    with open(QBOTJSON, "w") as f:
        json.dump(QBOT, f)
        print(f"{len(TWEETS)} tweets queued on '{QBOTJSON}'")

    # The end
    input(f"\nDone! ({round(time.time() - DELTA)}s)")
