#!/usr/bin/env python

import pandas as pd

from datetime import datetime

from pymongo import UpdateOne

from brand import groupIterable

from brand.parsers import get_data, add_logging_arguments, add_data_arguments, parse_arguments_with, setup_logger
from bson.code import Code

def custom_parser(parser):

    parser.add_argument('--batch-size',
                        default=1000,
                        type=int,
                        help="Batch size to be used when performing bulk enrich")

    return parser



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

def flatten(post):
    return {
        "_id": post["_id"],
        "count": post["value"]["count"],
        "first": datetime.fromtimestamp(post["value"]["min"]),
        "last": datetime.fromtimestamp(post["value"]["max"])
    }


if __name__ == "__main__":

    args = parse_arguments_with([add_data_arguments, add_logging_arguments, custom_parser])

    logger = setup_logger(args)

    data = get_data(args)

    posts = data["followers"]
    users = data["users"]

    db = data["db"]

    tmp_coll = "myresults"

    posts.map_reduce(map_f, reduce_f, tmp_coll)

    activities = pd.DataFrame( [flatten(post) for post in db[tmp_coll].find()] ).set_index("_id")

    db[tmp_coll].drop()

    activities["activity"] = (activities["last"] - activities["first"]).apply(lambda x: x.days) / activities["count"]

    batch_size = args.batch_size

    for ibatch, _users in enumerate(groupIterable(activities.iterrows(), batch_size)):

        logger.info("Batch %d: Processing %d users" % (ibatch, len(_users)))

        users.bulk_write(
            [UpdateOne({'username': user}, {"$set": {
                "activity": row["activity"],
                "first_post": row["first"],
                "last_post": row["last"]
            }}) for (user, row) in _users]
        )



