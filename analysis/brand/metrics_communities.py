import pandas as pd

from collections import Counter
from brand import dateGroupByKey, union, get_date

from brand.parsers import get_data, add_logging_arguments, add_data_arguments, parse_arguments_with, setup_logger

def filterNones(list):
    return [element for element in list if (element)]

def getBrandPipeline(brand_id, clusters, limit=None, start=None, end=None):
    return filterNones([{
        "$project": {"username": 1, "owner": 1, "hashtags": 1, "timestamp": 1, "mentions": 1},
    },
    { "$match": {"timestamp": {"$gte": pd.to_datetime(start)}}} if start is not None else start,
    { "$match": {"timestamp": {"$lt": pd.to_datetime(end)}}} if end is not None else end,
    {
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


def getCommunitySizes(start=None, end=None):
    return filterNones([{
        "$project": {"username": 1, "owner": 1, "timestamp": 1},
    }, {
        "$match": { "timestamp": {"$exists": True} }
    },
    {"$match": {"timestamp": {"$gte": pd.to_datetime(start)}}} if start is not None else start,
    {"$match": {"timestamp": {"$lt": pd.to_datetime(end)}}} if end is not None else end,
    {
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

def custom_parser(parser):

    parser.add_argument('--start', type=str, default=None)

    parser.add_argument('--end', type=str, default=None)

    parser.add_argument('--limit', type=int, default=None)

    parser.add_argument('--top-hashtags', type=int, default=10)

    parser.add_argument('--batch-size',
                        default=1000,
                        type=int,
                        help="Batch size to be used when performing bulk enrich")

    return parser


if __name__ == "__main__":

    from settings import brands

    args = parse_arguments_with([add_data_arguments, add_logging_arguments, custom_parser])

    logger = setup_logger(args)

    data = get_data(args)

    n = args.top_hashtags

    collection = data["posts"]

    clusters = {doc["id"]: doc["core_hashtags"][:n] for doc in data["community"].find()}

    brands_id = { b["username"]: b["id_user"] for b in data["brands"].find({}) }
    id_brands = { v: k for k, v in brands_id.items() }

    sizes = pd.DataFrame( list(collection.aggregate(getCommunitySizes(args.start, args.end))) )
    sizes["date"] = get_date(sizes)
    sizes["community"] = sizes["_id"].apply(lambda x: id_brands[x["community"]])
    cnt = sizes.set_index(["date", "community"])["count"]

    for brand in brands:

        id = brands_id[brand]

        print("Processing brand: %s (%d)" % (brand, id))

        pipe = getBrandPipeline(id, clusters, limit=args.limit, start=args.start, end=args.end)

        df = pd.DataFrame( list( collection.aggregate(pipe) ) )

        df["date"] = get_date(df)
        df["community"] = df["_id"].apply(lambda x: x["community"])

        for date, communities in df.groupby("date"):
            kpis = {
                str(row["community"]): {
                    "hashtags": dict(Counter(row["hashtags"]).most_common(n)),
                    "mentions": dict(Counter(row["mentions"]).most_common(n)),
                    "count": row["count"]
                } for _, row in communities.iterrows()
            }
            data["stats"].update({"brand": brand, "date": date},
                                 {"$set": {"communities": kpis, "community_size": cnt[(date, brand)]}},
                                 upsert=True)
