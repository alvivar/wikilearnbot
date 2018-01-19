"""
    Queues Wikipedia articles with images on Qbot.

    @matnesis
    2018/01/08
"""

import json
import os
import shutil
import sys
import time
from urllib.request import urlopen

from wikiapi import get_random_articles_with_images

# Deprecated, I keep this line to remember
# from wikiscrapper import get_random_wiki, get_wiki_summary

HOME = os.path.normpath(  # The script directory + cxfreeze compatibility
    os.path.dirname(
        sys.executable if getattr(sys, 'frozen', False) else __file__))

if __name__ == "__main__":

    DELTA = time.time()
    print("@wikilearnbot\n")

    # Config

    CONFIGJSON = os.path.join(HOME, "config.json")
    try:
        with open(CONFIGJSON, "r") as f:
            CONFIG = json.load(f)
    except (IOError, ValueError):
        CONFIG = {'image_size': 500, 'known_ids': []}

    # Qbot

    QBOTJSON = os.path.join(HOME, "qbot.json")
    try:
        with open(QBOTJSON, "r") as f:
            QBOT = json.load(f)
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
    WIKIS = get_random_articles_with_images(
        count=NEEDED,
        imagesize=CONFIG['image_size'],
        ignoreids=CONFIG['known_ids'])

    WIKISPATH = os.path.join(HOME, "wikis")
    if not os.path.exists(WIKISPATH):
        os.makedirs(WIKISPATH)

    with open(os.path.join(WIKISPATH, f"{round(time.time())}.json"), 'w') as f:
        json.dump(WIKIS, f)

    # Prepare messages and Download images

    IMGPATH = os.path.join(HOME, "images")
    if not os.path.exists(IMGPATH):
        os.makedirs(IMGPATH)

    TWEETS = []
    NEWIDS = []

    print("\nDownloading images...")
    for wiki in WIKIS:

        NEWIDS.append(wiki['pageid'])

        # Images

        imgfile = os.path.join(IMGPATH, os.path.basename(wiki['pageimageurl']))
        with urlopen(wiki['pageimageurl']) as r, open(imgfile, 'wb') as f:
            shutil.copyfileobj(r, f)
            print(f"Downloaded: {imgfile}")

        # Tweets

        desc = wiki['extract']
        desc = desc if len(desc) < 250 else f"{desc[:250]}[...]"

        TWEETS.append({'text': f"{desc} {wiki['pageurl']}", 'image': imgfile})

    # Config

    CONFIG['known_ids'] += NEWIDS

    with open(CONFIGJSON, 'w') as f:
        json.dump(CONFIG, f)
        print(f"\nArticles {NEWIDS} saved on: {CONFIGJSON}")

    # Qbot queue

    QBOT['messages'] = QBOT['messages'] + TWEETS

    with open(QBOTJSON, 'w') as f:
        json.dump(QBOT, f)
        print(f"{len(TWEETS)} tweets queued on: {QBOTJSON}")

    # The end

    print(f"\nDone! ({round(time.time() - DELTA)}s)")
