"""
    Queues Wikipedia articles with images on qbot.json as available.

    @matnesis
    2018/01/08
"""

import json
import os
import shutil
import sys
import time
import urllib.request
import random

from wikiscrapper import get_random_wiki, get_wiki_summary

HOME = os.path.normpath(  # The script directory + cxfreeze compatibility
    os.path.dirname(
        sys.executable if getattr(sys, 'frozen', False) else __file__))


def get_random_wikis(count, lang="en", wait=4):
    """
        Return a list with Wikipedia articles dictionaries that contains images.
    """
    wikis = []
    while count > 0:
        wiki = get_wiki_summary(
            get_random_wiki(language=lang), minimgsize=250, incfalseimg=True)

        url = list(wiki.keys())[0]
        imgs = list(wiki.values())[0]['images']
        if imgs:
            print(f"Added: {url}")
            wikis.append(wiki)
            count -= 1
        else:
            print(f"Discarded, no images: {url}")

        time.sleep(random.uniform(wait - 1, wait + 1))

    return wikis


if __name__ == "__main__":

    print("@wikilearnbot")
    DELTA = time.time()

    QBOTJSON = os.path.join(HOME, "qbot.json")
    try:
        QBOT = json.load(open(QBOTJSON, "r"))
    except (IOError, ValueError):
        print(f"QBot file not found:\n'{QBOTJSON}'")
        input()
        sys.exit(1)

    # Download wikis, one per schedule

    NEEDED = len(QBOT['schedule']['hours'])
    WIKIS = get_random_wikis(NEEDED)

    WIKISPATH = os.path.join(HOME, "wikis")
    if not os.path.exists(WIKISPATH):
        os.makedirs(WIKISPATH)

    with open(os.path.join(WIKISPATH, f"{round(time.time())}.json"), 'w') as f:
        json.dump(WIKIS, f)

    # Download images

    IMGPATH = os.path.join(HOME, "images")
    if not os.path.exists(IMGPATH):
        os.makedirs(IMGPATH)

    for wiki in WIKIS:
        for _, v in wiki.items():
            for imgk, _ in v['images'].items():

                imgfile = os.path.join(IMGPATH, os.path.basename(imgk))

                with urllib.request.urlopen(imgk) as r, open(imgfile,
                                                             'wb') as f:
                    shutil.copyfileobj(r, f)
                    print(f"Downloaded: '{imgfile}'")

    # QBot queue TODO

    # The end
    print(f"\nDone! ({round(time.time() - DELTA)}s)")
