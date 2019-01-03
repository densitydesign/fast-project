#!/usr/bin/env python
import re
from itertools import islice

def get_hashtags(text):
    return [hashtag.lower() for hashtag in re.findall(r"#(\w+)", text)]

def get_mentions(text):
    return [mention.lower() for mention in re.findall(r"(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9_]+)", text)]

from analysis.brand import groupIterable
from pymongo import MongoClient, UpdateOne

client = MongoClient('mongodb://localhost:27017/')
db = client['FaST']

post_coll = db["post_followers"]

batch_size=10000

cursor = post_coll.find({"$or": [{"hashtags": {"$exists": False}}, {"mentions": {"$exists": False}}]}, {"caption": 1})
# cursor = post_coll.find({}, {"caption": 1})

for ibatch, posts in enumerate(groupIterable(cursor, batch_size)):

    # text = post["caption"]
    # hashtags = [hashtag.lower() for hashtag in get_hashtags(text)]

    print("Batch %d: Processing %d posts" % (ibatch, len(posts)))

    documents = []
    for post in posts:
        try:
            documents.append(UpdateOne(
                {'_id': post["_id"]},
                {"$set": {"hashtags": get_hashtags(post["caption"]), "mentions": get_mentions(post["caption"])}}
            ))
        except Exception as e:
            print("Error for post id %s" % post["_id"])
            print("Exception: %s" % e.message)

    if len(documents)>0:
        post_coll.bulk_write(documents)


