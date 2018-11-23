#!/usr/bin/env python
import re
from itertools import islice


activity_query = [
    {
        "$match": { "taken_at_time": { "$exists" : True } }
    }, {
        "$addFields": {"str_len": {"$strLenCP": "$taken_at_time"}}
    }, {
        "$match": {"$expr": {"$ne": ["$str_len", 0]}}
    }, {
        "$addFields": { "time": {"$dateFromString": {"dateString": "$taken_at_time"}} }
    }, {
        "$group":
            {
                "_id": "$username",
                "first": {"$min": "$time"},
                "last": {"$max": "$time"},
                "count": {"$sum": 1}
            }
    }]


from bson.code import Code

map_f = Code("""function () {
    var date = parseInt(this.taken_at_timestamp);
    if ( date > 0) {
        emit(this.username, {"min": date, "max": date, "count": 1});
    }
}
""")

reduce_f = Code("""function(k,values) {
    
    reduced = {"min": values[0].min, "max": values[0].max, "count": values[0].count}
    // reduced = {"min": "", "max": "", "count": 0}
    
    for (var idx = 1; idx < values.length; idx++) {
        reduced.count += values[idx].count;
        if (reduced.min > values[idx].min) { reduced.min = values[idx].min }
        if (reduced.max < values[idx].max) { reduced.max = values[idx].max }
    }
    
    return reduced
}""")




import pandas as pd
from pymongo import MongoClient, UpdateOne

client = MongoClient('mongodb://localhost:27017/')
db = client['FaST']

posts = db["post_followers"]
users = db["user"]

tmp_coll = "myresults"

posts.map_reduce(map_f, reduce_f, tmp_coll)

from datetime import datetime

def flatten(post):
    return {
        "_id": post["_id"],
        "count": post["value"]["count"],
        "first": datetime.fromtimestamp(post["value"]["min"]),
        "last": datetime.fromtimestamp(post["value"]["max"])
    }

activities = pd.DataFrame( [flatten(post) for post in db[tmp_coll].find()] ).set_index("_id")

db[tmp_coll].drop()

activities["activity"] = (activities["last"] - activities["first"]).apply(lambda x: x.days) / activities["count"]

batch_size=1000

from analysis.brand import groupIterable

for ibatch, _users in enumerate(groupIterable(activities.iterrows(), batch_size)):

    # text = post["caption"]
    # hashtags = [hashtag.lower() for hashtag in get_hashtags(text)]

    print("Batch %d: Processing %d users" % (ibatch, len(_users)))

    users.bulk_write(
        [UpdateOne({'username': user}, {"$set": {
            "activity": row["activity"],
            "first_post": row["first"],
            "last_post": row["last"]
        }}) for (user, row) in _users]
    )



