from pymongo import MongoClient
import pandas as pd

from collections import Counter
from analysis.brand import dateGroupByKey, union, get_date

client = MongoClient()

db = client["FaST"]
c = db["post_followers"]

n = 10

clusters = {doc["id"]: doc["core_hashtags"][:n] for doc in db.community.find()}

def filterNones(list):
    return [element for element in list if (element)]

def getBrandPipeline(brand_id, limit=None):
    return filterNones([{
        "$project": {"username": 1, "owner": 1, "hashtags": 1, "timestamp": 1, "mentions": 1},
    }, {
        "$match": { "$and": [{"hashtags": {"$exists": True}},
                             {"mentions": {"$exists": True}},
                             {"timestamp": {"$exists": True}}]}
    }, {
        "$lookup":
            {
                "from": "user",
                "localField": "owner",
                "foreignField": "id_user",
                "as": "user_info"
            }
    }, {
        "$match": {"user_info.following" : brand_id}
    },
    {"$limit": limit} if limit is not None else limit,
    {
        "$addFields": {"communities": [{"id": k, "score": {"$size": {"$setIntersection": ["$hashtags", v]}}}
                                       for k, v in clusters.items()]}
    }, {
        "$project": {
            "mentions": 1,
            "hashtags": 1,
            "timestamp": 1,
            "communities": {
                "$filter": {
                    "input": "$communities",
                    "as": "item",
                    "cond": { "$gt": [ "$$item.score", 0 ] }
                }
            }
        }
    }, {
        "$match": { "$expr": {"$gt" : [{"$size": "$communities"}, 0]}}
    }, {
        "$unwind": "$communities"
    }, {
        "$group": {
            "_id": union({"community": "$communities.id"}, dateGroupByKey("$timestamp")),
            "hashtags": {"$push": "$hashtags"},
            "mentions": {"$push": "$mentions"},
            "count": {"$sum": 1}
        }
    }, {
        "$project": {
            "count": 1,
            "hashtags": {
                "$reduce": {
                    "input": "$hashtags",
                    "initialValue": [],
                    "in": { "$concatArrays" : ["$$value", "$$this"] }
                }
            },
            "mentions": {
                "$reduce": {
                    "input": "$mentions",
                    "initialValue": [],
                    "in": { "$concatArrays" : ["$$value", "$$this"] }
                }
            }
        }
    }
])


def getCommunitySizes():
    return filterNones([{
        "$project": {"username": 1, "owner": 1, "timestamp": 1},
    }, {
        "$match": { "timestamp": {"$exists": True} }
    }, {
        "$lookup":
            {
                "from": "user",
                "localField": "owner",
                "foreignField": "id_user",
                "as": "user_info"
            }
    }, {
        "$unwind": "$user_info"
    }, {
        "$unwind": "$user_info.following"
    }, {
        "$group": {
            "_id": union({"community": "$user_info.following"}, dateGroupByKey("$timestamp")),
            "count": {"$sum": 1}
        }
    }])

from analysis import brands

brands_id = { b["username"]: b["id_user"] for b in db.brand.find({}) }
id_brands = { v: k for k, v in brands_id.items() }

sizes = pd.DataFrame( list(c.aggregate(getCommunitySizes())) )
sizes["date"] = get_date(sizes)
sizes["community"] = sizes["_id"].apply(lambda x: id_brands[x["community"]])
cnt = sizes.set_index(["date", "community"])["count"]

for brand in brands:

    id = brands_id[brand]

    print("Processing brand: %s (%d)" % (brand, id))

    pipe = getBrandPipeline(id)

    df = pd.DataFrame( list( c.aggregate(pipe) ) )

    df["date"] = get_date(df)
    df["community"] = df["_id"].apply(lambda x: x["community"])

    for date, communities in df.groupby("date"):
        data = {
            str(row["community"]): {
                "hashtags": dict(Counter(row["hashtags"]).most_common(10)),
                "mentions": dict(Counter(row["mentions"]).most_common(10)),
                "count": row["count"]
            } for _, row in communities.iterrows()
        }
        db["stats"].update({"brand": brand, "date": date},
                           {"$set": {"communities": data, "community_size": cnt[(date, brand)]}},
                           upsert=True)