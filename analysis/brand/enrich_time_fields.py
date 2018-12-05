#!/usr/bin/env python
import re
from datetime import datetime
from itertools import islice

def get_time(timestamp):
    return datetime.fromtimestamp(int(float(timestamp)))

from analysis.brand import groupIterable
from pymongo import MongoClient, UpdateOne

client = MongoClient('mongodb://localhost:27017/')
db = client['FaST']

post_coll = db["post_followers"]

batch_size=10000

cursor = post_coll.find({"timestamp": {"$exists": False}}, {"taken_at_timestamp": 1})

for ibatch, posts in enumerate(groupIterable(cursor, batch_size)):

    print("Batch %d: Processing %d posts" % (ibatch, len(posts)))

    documents = []
    for post in posts:
        try:
            documents.append(UpdateOne(
                {'_id': post["_id"]},
                {"$set": {"timestamp": get_time(post["taken_at_timestamp"])}}
            ))
        except Exception as e:
            print("Error for post id %s" % post["_id"])
            print("Exception: %s" % e.message)

    if (len(documents)>0):
        post_coll.bulk_write(documents)