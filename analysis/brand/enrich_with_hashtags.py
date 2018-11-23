#!/usr/bin/env python
import re
from itertools import islice

def get_hashtags(text):
    return [hashtag.lower() for hashtag in re.findall(r"#(\w+)", text)]

def groupIterable(iterable, batch_size=10000):
    iterable = iter(iterable)
    return iter(lambda: list(islice(iterable, batch_size)), [])

from pymongo import MongoClient, UpdateOne

client = MongoClient('mongodb://localhost:27017/')
db = client['FaST']

post_coll = db["post_followers"]

batch_size=1000

cursor = post_coll.find({"hashtags": {"$exists": False}}, {"caption": 1})

for ibatch, posts in enumerate(groupIterable(cursor, batch_size)):

    # text = post["caption"]
    # hashtags = [hashtag.lower() for hashtag in get_hashtags(text)]

    print("Batch %d: Processing %d posts" % (ibatch, len(posts)))

    post_coll.bulk_write(
        [UpdateOne({'_id': post["_id"]}, {"$set": {"hashtags": get_hashtags(post["caption"])}}) for post in posts]
    )